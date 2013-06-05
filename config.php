<?php
require('globals.php'); /* where to set the local variables */

/* definition of local functions */
$local_functions = array('fmi' => 'fmi/local_functions_fmi.php',
			 'latmos' => 'latmos/local_functions_latmos.php');

/* definition of tree.xml per model */
$tree_url = array('fmi' => 'http://impex-fp7.fmi.fi/ws/FMI_HYB_tree.xml',
		  'latmos' => 'http://impex.latmos.ipsl.fr/tree.xml');

$models = array ('fmi' => 'FMI',
		 'latmos' => 'LATMOS');


?>