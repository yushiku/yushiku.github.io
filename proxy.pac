function user_proxy(url, host){

if( isInNet(myIpAddress(),"10.3.160.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.161.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.162.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.163.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.164.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.165.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.3.167.0","255.255.255.0")||
    isInNet(myIpAddress(),"10.239.138.0","255.255.255.0")){
  return "PROXY internal-182-vpn-elb-1434222708.ap-northeast-1.elb.amazonaws.com:8080";
}else{
  return "DIRECT";
}

}

function FindProxyForURL(url, host){

if( shExpMatch(host, "*c.microsoft.com") ||
    shExpMatch(host, "*download.windowsupdate.com") ||
    shExpMatch(host, "*fe3.delivery.mp.microsoft.com") ||
    shExpMatch(host, "*stats.update.microsoft.com") ||
    shExpMatch(host, "*update.microsoft.com") ||
    shExpMatch(host, "*windowsupdate.microsoft.com") ||
    shExpMatch(host, "*xmlrpc.rhn.redhat.com") ||
    shExpMatch(host, "*officeapps.live.com") ||
    shExpMatch(host, "*outlook.live.com") ||
    shExpMatch(host, "*outlook.office365.com") ||
    shExpMatch(host, "*onmicrosoft.com") ||
    shExpMatch(host, "*www.update.microsoft.com") ||
    shExpMatch(host, "*sls.update.microsoft.com") ||
    shExpMatch(host, "*fe2.update.microsoft.com") ||
    shExpMatch(host, "*fe1.update.microsoft.com") ||
    shExpMatch(host, "*v4.download.windowsupdate.com") ||
    shExpMatch(host, "*.digitalartscloud.com") ||
    shExpMatch(host, "*outlook.office.com") ||
    shExpMatch(host, "*skype.com") ||
    shExpMatch(host, "*.googlevideo.com") ||
    shExpMatch(host, "*google.com") ||
    true){
  return "DIRECT";
}

return user_proxy(url, host)

}
