<?php
include "includes/secret.inc";    if(array_key_exists("submit", $_POST)) {        if($secret == $_POST['secret']) {        print "Access granted. The password for natas7 is <censored>";    } else {        print "Wrong secret";    }    }