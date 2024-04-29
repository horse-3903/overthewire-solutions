<?php
session_start();
if (array_key_exists("submit", $_REQUEST)) {
    foreach ($_REQUEST as $key => $val) {
        $_SESSION[$key] = $val;
    }
}
if (array_key_exists("debug", $_GET)) {
    print "[DEBUG] Session contents:<br>";
    print_r($_SESSION);
}
$validkeys = array("align" => "center", "fontsize" => "100%", "bgcolor" => "yellow");
$form = "";
$form .= '<form action="index." method="POST">';
foreach ($validkeys as $key => $defval) {
    $val = $defval;
    if (array_key_exists($key, $_SESSION)) {
        $val = $_SESSION[$key];
    } else {
        $_SESSION[$key] = $val;
    }
    $form .= "$key: <input name='$key' value='$val' /><br>";
}
$form .= '<input type="submit" name="submit" value="Update" />';
$form .= '</form>';
$style = "background-color: " . $_SESSION["bgcolor"] . "; text-align: " . $_SESSION["align"] . "; font-size: " . $_SESSION["fontsize"] . ";";
$example = "<div style='$style'>Hello world!</div>";