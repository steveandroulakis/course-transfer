<?php

// This script notifies students who have requested to be told when a course is open for transfers

// Turn error reporting on
error_reporting(-1);
ini_set('display_errors', 'On');

// Include the phpmailer library
require ("/var/www/html/libraries/vendor/phpmailer/phpmailer/PHPMailerAutoload.php");

// Go through the notifications table and only look for records that have unsent notifications
// Connect to the mysql server
$db = new mysqli("teamfast.online","coursetransfer","monash123","ct");

if ($db)
{
	// Access the notifications table and go through each record
	$result = $db->query("SELECT * FROM fabrik_notifications WHERE status=\"UNSENT\"");
	// Go through the records from the top
    $result->data_seek(0);

	// Loop through the records
	while ($row = $result->fetch_assoc())
	{
		// Check if the course is open, if it is, send the email and set this record as sent
		$course_details = $db->query("SELECT * FROM fabrik_courses WHERE course_code=\"{$row['course_code']}\" LIMIT 1");
		$course_details_result = $course_details->fetch_assoc();

		if ($course_details_result["course_status"] == "OPEN")
		{
			// Build the email
			// Access the student's name and email address for the email
			$student_details = $db->query("SELECT name, email FROM n4uzb_users WHERE id={$row['userid']} LIMIT 1");
			$student_details_result = $student_details->fetch_assoc();
			
			$mail = new PHPMailer;
			$mail->setFrom("adm-do-not-reply@monash.edu", "Monash University Course transfers");
			$mail->addAddress($student_details_result["email"], $student_details_result["name"]);
			$mail->Subject = "Course transfers now available for {$course_details_result['course_title']} ({$course_details_result['course_code']})";
			$mail->Body = "Hi {$student_details_result['name']}, this is a notification that the course {$course_details_result['course_title']} ({$course_details_result['course_code']}) is now accepting applications for course transfers.";

			// Send the message and check for errors
			if (!$mail->send())
			{
				echo "Mailer error: " . $mail->ErrorInfo;
			}

			// Set the notification as sent
			if (!$db->query("UPDATE fabrik_notifications SET status=\"SENT\" WHERE id={$row['id']}"))
			{
				echo "Error updating table: ".$db->error;
			}
		}
	}
}

?>