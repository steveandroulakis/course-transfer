<?php

// This script is called by the cron to update the status of courses to make them open or closed

// Turn error reporting on
error_reporting(-1);
ini_set('display_errors', 'On');

// Connect to the mysql server
$db = new mysqli("teamfast.online","coursetransfer","monash123","ct");

if ($db)
{
	$today = date("Y-m-d H:i:s");

	// Access the table and go through each record
	$result = $db->query("SELECT * FROM fabrik_courses");
	// Go through the records from the top
    $result->data_seek(0);

	// Loop through the records and update the status if need be
	while ($row = $result->fetch_assoc())
	{
    	// If there's no start date, treat it as today
        if (($row["facs_start"] == NULL) || ($row["facs_start"] == ""))
        {
        	$row["facs_start"] == date("Y-m-d") . " 00:00:00";
        }

    	// Only update the status if there is an end date
        if (($row["facs_end"] != NULL) && ($row["facs_end"] != ""))
        {
			// Check if today's date is in range of the open and close dates
            if (($today >= $row["facs_start"]) && ($today <= $row["facs_end"]))
            {
				// Set the status to open
				if (!$db->query("UPDATE fabrik_courses SET course_status=\"OPEN\" WHERE id={$row['id']}"))
                {
                	echo "Error updating table: ".$db->error;
                }
            }
            else
            {
				// Set the status to closed
                if (!$db->query("UPDATE fabrik_courses SET course_status=\"CLOSED\" WHERE id={$row['id']}"))
                {
                	echo "Error updating table: ".$db->error;
                }
            }
        }
	}
}



