<?php
require_once('Zend/Soap/AutoDiscover.php');
require_once('Zend/Soap/Server.php');
require_once('Zend/Soap/Wsdl.php');
require_once('IMPExMethods.php');
$wsdl = new Zend_Soap_Autodiscover('Zend_Soap_Wsdl_Strategy_ArrayOfTypeComplex');
$wsdl->setClass('IMPExMethods');
if (isset($_GET['wsdl'])) 
  {
    $wsdl->handle();
  } 
else 
  {
    $server = new Zend_Soap_Server($server.'IMPExServer.php?wsdl'); /*TODO: check why I'm changing the server variable!! */
    $server->setClass('IMPExMethods');
    $server->setEncoding('ISO-8859-1');
    $server->handle();
  }

?>