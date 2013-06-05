<?php
require_once('Zend/Soap/AutoDiscover.php');
require_once('Zend/Soap/Server.php');
require_once('Zend/Soap/Wsdl.php');
require_once('IMPExMethods.php');
$wsdl = new Zend_Soap_Autodiscover();
$wsdl->setClass('IMPExMethods');
if (isset($_GET['wsdl'])) 
  {
    $wsdl->handle();
  } 
else 
  {
    $server = new Zend_Soap_Server($server.'IMPExServer.php?wsdl');
    $server->setClass('IMPExMethods');
    $server->setEncoding('ISO-8859-1');
    $server->handle();
  }

?>