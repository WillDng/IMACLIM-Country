//////  Copyright or © or Copr. Ecole des Ponts ParisTech / CNRS 2018
//////  Main Contributor (2017) : Gaëlle Le Treut / letreut[at]centre-cired.fr
//////  Contributors : Emmanuel Combet, Ruben Bibas, Julien Lefèvre
//////  
//////  
//////  This software is a computer program whose purpose is to centralise all  
//////  the IMACLIM national versions, a general equilibrium model for energy transition analysis
//////
//////  This software is governed by the CeCILL license under French law and
//////  abiding by the rules of distribution of free software.  You can  use,
//////  modify and/ or redistribute the software under the terms of the CeCILL
//////  license as circulated by CEA, CNRS and INRIA at the following URL
//////  "http://www.cecill.info".
//////  
//////  As a counterpart to the access to the source code and  rights to copy,
//////  modify and redistribute granted by the license, users are provided only
//////  with a limited warranty  and the software's author,  the holder of the
//////  economic rights,  and the successive licensors  have only  limited
//////  liability.
//////  
//////  In this respect, the user's attention is drawn to the risks associated
//////  with loading,  using,  modifying and/or developing or reproducing the
//////  software by the user in light of its specific status of free software,
//////  that may mean  that it is complicated to manipulate,  and  that  also
//////  therefore means  that it is reserved for developers  and  experienced
//////  professionals having in-depth computer knowledge. Users are therefore
//////  encouraged to load and test the software's suitability as regards their
//////  requirements in conditions enabling the security of their systems and/or 
//////  data to be ensured and,  more generally, to use and operate it in the
//////  same conditions as regards security.
//////  
//////  The fact that you are presently reading this means that you have had
//////  knowledge of the CeCILL license and that you accept its terms.
//////////////////////////////////////////////////////////////////////////////////

// main executable script

//PREAMBULE
exec ("preambule.sce");

disp("=====IMACLIM-S========");
 
/////////////////////////////////////////////////////////////////////////////////////////////
//	STEP 0: SYSTEM DEFINITION & SAVEDIR SETUP
/////////////////////////////////////////////////////////////////////////////////////////////
disp("STEP 0: loading Dashboard ");
exec("Dashboard.sce");

runName = study + "_" + mydate();
SAVEDIR = OUTPUT+ runName + filesep();
mkdir(SAVEDIR);
diary(SAVEDIR+"summary.log");

SAVEDIR_IOA = OUTPUT+ runName + filesep()+ "outputs_IOA"+filesep();
mkdir(SAVEDIR_IOA);

printf("===============================================\n");
printf("===== IMACLIM-S is running=============================\n");
printf("===============================================\n");

disp(" ======= for resolving the system: "+System_Resol)
printf("===============================================\n");
disp(" ======= using the study file: "+study)
printf("===============================================\n");
disp("======= with various class of households: "+H_DISAGG)
printf("===============================================\n");
disp("======= at aggregated level: "+AGG_type)
printf("===============================================\n");

/////////////////////////////////////////////////////////////////////////////////////////////
//	STEP 1: LOADING DATA
/////////////////////////////////////////////////////////////////////////////////////////////

disp("STEP 1: DATA...");
exec("Loading_data.sce");
// exec("Loading_params.sce");

exec("IOT_DecompImpDom.sce");
 
//Execute Households_Disagg.sce file if Index_HouseholdsDISAGG is defined
if	H_DISAGG <> "HH1"
	exec("Households_Desag.sce");
end


//Execute agreagation.sce file if Index_SectorsAGG is defined
if AGG_type <> ""
    exec("Aggregation.sce");
    exec("Hybridisation.sce" );
end

exec("Loading_params.sce");

/////////////////////////////////////////////////////////////////////////////////////////////
//	STEP 2: CHECKING BENCHMARK DATA
/////////////////////////////////////////////////////////////////////////////////////////////
disp("STEP 2: CHECKING CONSISTENCY of BENCHMARK DATA...")
exec("Checks_loads.sce");

/////////////////////////////////////////////////////////////////////////////////////////////
//	STEP 3: CALIBRATION
/////////////////////////////////////////////////////////////////////////////////////////////

disp("STEP 3: CODE CALIBRATION...");
exec("Check_CalibSyst.sce");
exec("Calibration.sce");

////////////////////////////////////////////////////////////
// 	STEP 4: INPUT OUTPUT ANALYSIS BY
////////////////////////////////////////////////////////////
disp("STEP 4: INPUT OUTPUT ANALYSIS FOR EMBODIED EMISSIONS AT BASE YEAR");
exec(CODE+"IOA_BY.sce");

////////////////////////////////////////////////////////////
// 	STEP 5: RESOLUTION - EQUILIBRIUM
////////////////////////////////////////////////////////////

disp("STEP 5: RESOLUTION AND EQUILIBRIUM...");
exec(System_Resol+".sce");

////////////////////////////////////////////////////////////
// 	STEP 6: OUTPUT EXTRACTION AND RESULTS DISPLAY
////////////////////////////////////////////////////////////

disp("STEP 6: OUTPUT EXTRACTION AND RESULTS DISPLAY...");
exec(CODE+"outputs.sce");
exec(CODE+"outputs_indic.sce");

if	System_Resol == "Projection_ECOPA"
	exec(CODE+"outputs_indic_ECOPA.sce");
end

////////////////////////////////////////////////////////////
// 	STEP 7: INPUT OUTPUT ANALYSIS AFTER RUN
////////////////////////////////////////////////////////////
disp("STEP 7: INPUT OUTPUT ANALYSIS FOR EMBODIED EMISSIONS...");
// exec(CODE+"IOA_Run.sce");