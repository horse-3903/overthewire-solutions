<?php
function setLanguage()
{
        if (array_key_exists("lang", $_REQUEST)) if (safeinclude("language/" . $_REQUEST["lang"]))
                return 1;
        safeinclude("language/en");
}
function safeinclude($filename)
{
        if (strstr($filename, "../")) {
                logRequest("Directory traversal attempt! fixing request.");
                $filename = str_replace("../", "", $filename);
        }
        if (strstr($filename, "natas_webpass")) {
                logRequest("Illegal file access detected! Aborting!");
                exit(-1);
        }
        if (file_exists($filename)) {
                include ($filename);
                return 1;
        }
        return 0;
}
function listFiles($path)
{
        $listoffiles = array();
        if ($handle = opendir($path))
                while (false !== ($file = readdir($handle)))
                        if ($file != "." && $file != "..")
                                $listoffiles[] = $file;
        closedir($handle);
        return $listoffiles;
}
function logRequest($message)
{
        $log = "[" . date("d.m.Y H::i:s", time()) . "]";
        $log = $log . " " . $_SERVER['HTTP_USER_AGENT'];
        $log = $log . " \"" . $message . "\"\n";
        $fd = fopen("/var/www/natas/natas25/logs/natas25_" . session_id() . ".log", "a");
        fwrite($fd, $log);
        fclose($fd);
}
foreach (listFiles("language/") as $f)
        echo "<option>$f</option>";
session_start();
setLanguage();
echo "<h2>$__GREETING</h2>";
echo "<p align=\"justify\">$__MSG";
echo "<div align=\"right\"><h6>$__FOOTER</h6><div>";