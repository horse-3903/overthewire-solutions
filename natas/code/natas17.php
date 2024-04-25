<?php
/*CREATE TABLE `users` (  `username` varchar(64) DEFAULT NULL,  `password` varchar(64) DEFAULT NULL);*/ 

if (array_key_exists("username", $_REQUEST)) {
    $link = mysqli_connect('localhost', 'natas17', '<censored>');
    mysqli_select_db($link, 'natas17');
    $query = "SELECT * from users where username=\"" . $_REQUEST["username"] . "\"";
    if (array_key_exists("debug", $_GET)) {
        echo "Executing query: $query<br>";
    }
    $res = mysqli_query($link, $query);
    if ($res) {
        if (mysqli_num_rows($res) > 0) {
        } else {
        }
    } else {
    }
    mysqli_close($link);
} else {
}