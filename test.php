<?php
error_reporting(-1);
ini_set('display_errors', 'On');
//phpinfo();

$db = new mysqli("teamfast.online","coursetransfer","monash123");

if ($db)
{
	echo $db->host_info;
}


require ("/var/www/html/libraries/vendor/phpmailer/phpmailer/PHPMailerAutoload.php");

$mail = new PHPMailer;
//$mail->isSMTP()
$mail->setFrom("adm-do-not-reply@monash.edu", "Monash University Course Transfers");
$mail->addAddress("greg.mckeown@monash.edu");
$mail->Subject = "Course transfer";
$mail->Body = "This is a plain-text message body";

//send the message, check for errors
if (!$mail->send()) {
    echo "Mailer Error: " . $mail->ErrorInfo;
} else {
    echo "Message sent!";
}




?>