
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ECONOMIC EQUATIONS for projection
//

// - mettre les ConstrainedShare_C = 0
parameters.ConstrainedShare_C(Indice_EnerSect, :) = 0;

// - Techniques Asymptotes in production
parameters.ConstrainedShare_IC(Indice_EnerSect,:) = parameters.ConstrainedShare_IC(Indice_EnerSect,:);
// parameters.ConstrainedShare_IC(Indice_EnerSect,find(Index_Sectors<> "Composite")) = 0.5*parameters.ConstrainedShare_IC(Indice_EnerSect,find(Index_Sectors<> "Composite"));
// parameters.ConstrainedShare_IC(Indice_EnerSect,find(Index_Sectors== "Composite")) = 0.45*parameters.ConstrainedShare_IC(Indice_EnerSect,find(Index_Sectors== "Composite"));




// - sigma_ConsoBudget = 1
parameters.sigma_ConsoBudget = 1 ; 

// - calculer u_tot

// - calculer la Labour_Product (productivité du travail)
parameters.time_since_BY = 5 ; // Changing projection horizon from 20y to 5y
// parameters.Mu = 1;
// Labour_Product = (1 + parameters.Mu)^time_period ; 

// parameters.Carbon_Tax_rate = 1e5;

/// GDP in 2015 - thousand of euro 2010 - source : Insee 
/// GDP in 2015 - thousand of SAR 2010 - source: GSTAT -Salah
GDP_2015 = 2350373 * 10^3 ;

////// Source: SNBC - Reference scénario (AMS2)
// From 2016-2020 ( adapt to 2015 here) 
// GDP_rate1 = 1.6 ;
// GDP_2020 = GDP_2015*(  GDP_rate1/100 + 1)^(2020-2015) ; 
// From 2021-2025 
// GDP_rate2 = 1.9 ; 
// GDP_2025 = GDP_2020*(  GDP_rate2/100 + 1)^(2025-2020) ;
// From 2026-2030 
// GDP_rate3 = 1.7 ; 
// GDP_2030 = GDP_2025*(  GDP_rate3/100 + 1)^(2030-2025) ;
// From 2031-2035 
// GDP_rate4 = 1.6 ;
// GDP_2035 = GDP_2030*(  GDP_rate4/100 + 1)^(2035-2030) ;
/// GDP unit : thousand of euro 2010


// Labour force  2035 -  units : thousand of people - Source : from INSEE 
Labour_force_2015  = 11823.876; // Labour_force in the private sector : 10575818 ; in the Gov : 1248058
//Labour_force_2035  = 30122;

Labour_force_proj =  Labour_force_2015 ;
GDP_proj = GDP_2015 ; 

// Estimation du nombre de personnes employées (avec taux de chômage historique) : Labour_force_2035 * ( 1 - u_tot_ref ) ;
// Estimation du nombre d'équivalent temps plein : Labour_force_2035 * ( 1 - u_tot_ref ) * LabourByWorker_coef;

// Labour producitivy level compared to base year - as used in equations
Labour_Product = ( GDP_proj / BY.GDP )  / ( ( Labour_force_proj * ( 1 - BY.u_tot ) * BY.LabourByWorker_coef ) / sum(BY.Labour) ) ;

Deriv_Exogenous.Labour_force =  (Labour_force_proj / sum(BY.Labour_force)) * BY.Labour_force ;

parameters.Mu =  Labour_Product^(1/parameters.time_since_BY) - 1 ;
parameters.phi_L =  ones(parameters.phi_L)*parameters.Mu;


// - voir si Distribution_Shares(Indice_Labour_Income, Indice_Households) 
// change


//	Import prices are exogenous but evolve like domestic prices
// pM = pM * Labour_Product

///////////////////////////////////////////////
//// Demography 
///////////////////////////////////////////////
// Deriv_calib.Population_ref = Population;
/// Population 2035 - in thousand of people - Source: from INSEE ('projection de population à 2070')
Population_2015 = 31521 ; 
/// Population 2035 - in thousand of people - Source: from SNBC 
//Population_2035 = 71680 ; 

Population_proj = Population_2015;

Deriv_Exogenous.Population =  (Population_proj / sum(BY.Population)) *BY.Population ;
 
// Population_growth_rate = (Population_2035 - initial_value.Population) / initial_value.Population ; 

// Proj : Pop = (1+ delta)^t * popo initial
//	Voir pou pop totele et pop active

/// Number of people by household class
 // Population = Population*(1 + Population_growth_rate)^t ;

 // Retired = Retired*(1 + Retired_growth_rate)^t ; 
 // homothetique : Retired_growth_rate=0
///////////////////////////////////////////////
//// Prices
///////////////////////////////////////////////

// u_tot = u_tot_proj
//	Le taux de chômage n'est plus une variable dans la proj (drop wage curve)
// il faut retirer u_tot des variables du systeme / et retirer la fonction

///////////////////////////////////////////////
//// Final demand
///////////////////////////////////////////////


///////////////////////////////////////////////
//// Production
///////////////////////////////////////////////
// Labour_Product = (1 + Population_growth_rate)^t ;

///////////////////////////////////////////////
//// Trade
///////////////////////////////////////////////



