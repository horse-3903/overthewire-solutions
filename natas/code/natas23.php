<?php
if (array_key_exists("passwd", $_REQUEST)) {
    if (strstr($_REQUEST["passwd"], "iloveyou") && ($_REQUEST["passwd"] > 10)) {
        echo "<br>The credentials for the next level are:<br>";
        echo "<pre>Username: natas24 Password: <censored></pre>";
    } else {
        echo "<br>Wrong!<br>";
    }
}