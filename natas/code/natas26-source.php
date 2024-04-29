<?php
class Logger
{
    private $logFile;
    private $initMsg;
    private $exitMsg;
    function __construct($file)
    {
        $this->initMsg = "#--session started--#\n";
        $this->exitMsg = "#--session end--#\n";
        $this->logFile = "/tmp/natas26_" . $file . ".log";
        $fd = fopen($this->logFile, "a+");
        fwrite($fd, $this->initMsg);
        fclose($fd);
    }
    function log($msg)
    {
        $fd = fopen($this->logFile, "a+");
        fwrite($fd, $msg . "\n");
        fclose($fd);
    }
    function __destruct()
    {
        $fd = fopen($this->logFile, "a+");
        fwrite($fd, $this->exitMsg);
        fclose($fd);
    }
}
function showImage($filename)
{
    if (file_exists($filename))
        echo "<img src=\"$filename\">";
}
function drawImage($filename)
{
    $img = imagecreatetruecolor(400, 300);
    drawFromUserdata($img);
    imagepng($img, $filename);
    imagedestroy($img);
}
function drawFromUserdata($img)
{
    if (array_key_exists("x1", $_GET) && array_key_exists("y1", $_GET) && array_key_exists("x2", $_GET) && array_key_exists("y2", $_GET)) {
        $color = imagecolorallocate($img, 0xff, 0x12, 0x1c);
        imageline($img, $_GET["x1"], $_GET["y1"], $_GET["x2"], $_GET["y2"], $color);
    }
    if (array_key_exists("drawing", $_COOKIE)) {
        $drawing = unserialize(base64_decode($_COOKIE["drawing"]));
        if ($drawing)
            foreach ($drawing as $object)
                if (array_key_exists("x1", $object) && array_key_exists("y1", $object) && array_key_exists("x2", $object) && array_key_exists("y2", $object)) {
                    $color = imagecolorallocate($img, 0xff, 0x12, 0x1c);
                    imageline($img, $object["x1"], $object["y1"], $object["x2"], $object["y2"], $color);
                }
    }
}
function storeData()
{
    $new_object = array();
    if (array_key_exists("x1", $_GET) && array_key_exists("y1", $_GET) && array_key_exists("x2", $_GET) && array_key_exists("y2", $_GET)) {
        $new_object["x1"] = $_GET["x1"];
        $new_object["y1"] = $_GET["y1"];
        $new_object["x2"] = $_GET["x2"];
        $new_object["y2"] = $_GET["y2"];
    }
    if (array_key_exists("drawing", $_COOKIE)) {
        $drawing = unserialize(base64_decode($_COOKIE["drawing"]));
    } else {
        $drawing = array();
    }
    $drawing[] = $new_object;
    setcookie("drawing", base64_encode(serialize($drawing)));
}
session_start();
if (array_key_exists("drawing", $_COOKIE) || (array_key_exists("x1", $_GET) && array_key_exists("y1", $_GET) && array_key_exists("x2", $_GET) && array_key_exists("y2", $_GET))) {
    $imgfile = "img/natas26_" . session_id() . ".png";
    drawImage($imgfile);
    showImage($imgfile);
    storeData();
}