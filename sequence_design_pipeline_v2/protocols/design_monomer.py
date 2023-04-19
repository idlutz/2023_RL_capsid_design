def make_script(pssm_f):
    xml = f"""
<ROSETTASCRIPTS> 
  <SCOREFXNS>
    <ScoreFunction name="sfxn_clean" weights="beta_nov16"/>
    <ScoreFunction name="sfxn_clean_cst" weights="beta_nov16_cst"/>

    <ScoreFunction name="sfxn_design" weights="beta_nov16">
        <Reweight scoretype="approximate_buried_unsat_penalty" weight="5"/>
        <Set approximate_buried_unsat_penalty_burial_atomic_depth="3.5"/>
        <Set approximate_buried_unsat_penalty_hbond_energy_threshold="-0.5"/>
        <Set approximate_buried_unsat_penalty_hbond_bonus_cross_chain="-1"/>
        <Reweight scoretype="res_type_constraint" weight="1.0"/>
        <Reweight scoretype="arg_cation_pi" weight="3"/>
    </ScoreFunction>

  </SCOREFXNS>

  <TASKOPERATIONS>
    <LimitAromaChi2 name="limitchi2" chi2max="110" chi2min="70" include_trp="True" />
    <ExtraRotamersGeneric name="ex1_ex2" ex1="1" ex2aro="1"/>
    <SeqprofConsensus name="pssm_design" filename="{pssm_f}" min_aa_probability="-0.5" convert_scores_to_probabilities="0" probability_larger_than_current="0" debug="1" ignore_pose_profile_length_mismatch="1"/>
    PruneBuriedUnsats name="prune_buried_unsats" allow_even_trades="false" atomic_depth_cutoff="4.0" />
  </TASKOPERATIONS>

  <RESIDUE_SELECTORS>
    <Task name="pssm_resis" designable="true" task_operations="pssm_design" />
    <SecondaryStructure name="loops" ss="L"/>
    <SecondaryStructure name="helices" ss="H"/>
    <Neighborhood name="around_loops" distance="6.0" selector="loops"/>
    <Not name="not_around_loops" selector="around_loops"/>
    <ResidueName name="polar_aas" residue_name3="SER,THR,ASN,GLN,HIS,TYR,TRP,ASP" />
    <And name="hbnets_around_loops" selectors="around_loops,polar_aas"/>
    <ResiduePDBInfoHasLabel name="hbnet_residues" property="HBNet" />
    <Layer name="hbnet_core" select_core="true" core_cutoff="3.3" />
    <Neighborhood name="around_hbnet" selector="hbnet_residues" distance="5.0" />
    <And name="core_around_hbnet" selectors="hbnet_core,around_hbnet"/>
    <Layer name="core" use_sidechain_neighbors="true" core_cutoff="4.9" surface_cutoff="2.7" sc_neighbor_dist_exponent="0.7" select_core="true" />
    <Layer name="boundary" use_sidechain_neighbors="true" core_cutoff="4.9" surface_cutoff="2.7" sc_neighbor_dist_exponent="0.7" select_boundary="true" />
    <Layer name="surface" use_sidechain_neighbors="true" core_cutoff="4.9" surface_cutoff="2.7" sc_neighbor_dist_exponent="0.7" select_surface="true" />
    <Chain name="chainA" chains="A" />
    <And name="int_resis_chainA" selectors="chainA" />
  </RESIDUE_SELECTORS>

  <MOVERS>
    <FavorSequenceProfile name="FSP" scaling="none" weight="1" pssm="{pssm_f}" scorefxns="sfxn_design"/>
      
    <FastDesign name="fastdes" repeats="3" relaxscript="InterfaceDesign2019" scorefxn="sfxn_design" task_operations="limitchi2,pssm_design"> ex1_ex2
        <MoveMap name="map" bb="1" chi="1" jump="1"/>
    </FastDesign>

    <DumpPdb name="dump" fname="dumping_built" tag_time="True"/>
  </MOVERS>

  <FILTERS>
    ClashCheck name="clash_check" clash_dist="2" nsub_bblock="1" cutoff="2" verbose="1" write2pdb="1" confidence="0"/>

    <BuriedUnsatHbonds name="vbuns_all_heavy" report_all_heavy_atom_unsats="true" scorefxn="sfxn_clean" ignore_surface_res="false" print_out_info_to_pdb="true" atomic_depth_selection="5.5" burial_cutoff="1000" confidence="0" />
    <BuriedUnsatHbonds name="sbuns_all_heavy" report_all_heavy_atom_unsats="true" scorefxn="sfxn_clean" cutoff="4" residue_surface_cutoff="20.0" ignore_surface_res="true" print_out_info_to_pdb="true" dalphaball_sasa="1" probe_radius="1.1" atomic_depth_selection="5.5" atomic_depth_deeper_than="false" confidence="0" />

    <ResidueCount name="res_count_all" max_residue_count="9999" confidence="0"/>
    <ScoreType name="total_score" scorefxn="sfxn_clean" threshold="0" confidence="0"/>
    <CalculatorFilter name="score_per_res" equation="total_score / res" threshold="-2.5" confidence="0">
      <Var name="total_score" filter="total_score"/>
      <Var name="res" filter="res_count_all"/>
    </CalculatorFilter>
    <Time name="timed"/>
    <Sasa name="sasa" threshold="200" upper_threshold="2000" hydrophobic="0" polar="0" confidence="0" />
    Ddg name="ddG" repeats="1" extreme_value_removal="0" translate_by="1000" scorefxn="sfxn_clean" task_operations="ex1_ex2,limitchi2,pssm_design" repack="1" threshold="0" relax_mover="min_clean_no_rb" repack_bound="0" relax_bound="0" repack_unbound="1" relax_unbound="1" confidence="0" />
    <SecondaryStructureCount name="ss_count" filter_helix_sheet="1" num_helix_sheet="2" min_helix_length="4" min_sheet_length="3" min_loop_length="1" return_total="1" confidence="0" residue_selector="core" min_element_resis="3" />
    <ResidueCount name="AlaCount" residue_types="ALA"         residue_selector="core" max_residue_count="5" confidence="0" />
    <ResidueCount name="MetCount" residue_types="MET"         residue_selector="core" max_residue_count="5" confidence="0" />
    <ResidueCount name="HPcCount" residue_types="VAL,LEU,ILE"   residue_selector="core" max_residue_count="20" confidence="0" />
    <ResidueCount name="AroCount" residue_types="TRP,PHE,TYR,HIS" residue_selector="core" max_residue_count="6" confidence="0" />
    <Geometry name="geom" count_bad_residues="true" confidence="0"/>
  </FILTERS>


  <PROTOCOLS>
    <Add filter_name="timed" />
  
    // generate and sample docked configurations
    <Add mover="FSP"/>

    // pre-design filters
    Add filter="clash_check"/>
    Add filter_name="sasa" />
    Add filter_name="ss_count" />

    // fastdesign and dump pdb for debugging
    <Add mover="fastdes"/>

    // postfilters
    Add filter="clash_check"/>
    <Add filter="res_count_all"/>
    <Add filter="total_score"/>
    <Add filter="score_per_res" />
    <Add filter="vbuns_all_heavy"/>
    <Add filter="sbuns_all_heavy"/>
    <Add filter_name="ss_count" />
    <Add filter_name="geom" />

    // run_metrics
    <Add filter_name="AlaCount" />
    <Add filter_name="MetCount" />
    <Add filter_name="HPcCount" />
    <Add filter_name="AroCount" />

    <Add filter_name="timed" />
  </PROTOCOLS>

</ROSETTASCRIPTS>
"""
    return xml