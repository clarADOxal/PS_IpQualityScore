# ─── LABEL CREATION ────────────────────────────────────────────────
cls
$Name="PS_IpQualityScore"
$version="6.0"
$Creation_Date = "18:36 17/08/2025"

#Delete unused method
#--------------------
$Creation_How = "Full Humain Brain"

#Logo Exemple
#------------
$Logo =" (\_/)`n (OvO)`n//uuu\\`nV\UUU/V`n ^^ ^^"

#Todo
#----
$Todo="A identifier"
$Todo+=""

# Label
#-------
if (($Name.Length) -gt ($version.Length)){
	$fior1=$Name.Length+10;
	$fior2=($name.length)-($name.length)
    $fior3=($name.length)-($version.length)
} else {
    $fior1=$version.length+10;
    $fior2=($version.length)-($name.length)
    $fior3=(($version.length)-($version.length))
}

$fior1result="";for ($j=1; $j -le $fior1; $j++) { $fior1result+="#" }
$fior2result="";for ($j=1; $j -le $fior2; $j++) { $fior2result+=" " }
$fior3result="";for ($j=1; $j -le $fior3; $j++) { $fior3result+=" " }

write-host $fior1result
write-host "####"$Name$fior2result" ####"
write-host "####"$version$fior3result" ####"
write-host $fior1result
get-date -displayHint Time
write-host $Logo

Start-Sleep 1


# ─── CONFIGURATION ────────────────────────────────────────────────

#API KEY (https://www.ipqualityscore.com/create-account)
#===================================

############################################ VVVVVVVVV ##############################

$API_KEY = ""

############################################ AAAAAAAAA ##############################

if ($API_KEY -eq ""){Write-host -f red "Complete API KEY into source code";Sleep;return}

#Incoming file
#===================================
write-host ""
Write-host "Prepare a file with all IP to search (1 by line)"
write-host ""

$proj = Read-Host -Prompt 'Drag & Drop file to analyze '
$proj=$proj -replace '"', ""

#Folder Name
$folderPath = Split-Path $proj

#File Name
$fileName = Split-Path $proj -Leaf
write-host -fore green $proj

#Date
#====
$ExecutionDate=Get-Date -Format "yyyy.MM.dd_HH.mm.ss"


#Out folder
#===================================
$out_folder	="OUT"

If(!(test-path $out_folder)){New-Item -Path $out_folder	 -ItemType Directory}

$exitfile=$folderPath+"\"+$out_folder+"\"+$fileName+"_"+ $ExecutionDate+"_result_fraudscore.csv"


cls

# ─── RUN JOB ────────────────────────────────────────────────


$Datas = @()

$numberofline = @(Get-Content $proj).Length
write-host -fore green $numberofline

get-content $proj | Sort-Object | Get-Unique | %{
$URL = "https://ipqualityscore.com/api/json/ip/"+$API_KEY+"/"+$_
#sleep
$result = (ConvertFrom-Json ((Invoke-WebRequest -Uri $URL).Content))

#write-host $URL
#write-host $fraud_score

$item = New-Object PSObject
$item | Add-Member -type NoteProperty -Name 'IP' -Value $_
$item | Add-Member -type NoteProperty -Name 'fraudscore' -Value $result.fraud_score
$item | Add-Member -type NoteProperty -Name 'success' -Value $result.success
$item | Add-Member -type NoteProperty -Name 'message' -Value $result.message 
$item | Add-Member -type NoteProperty -Name 'country_code' -Value $result.country_code 
$item | Add-Member -type NoteProperty -Name  'region' -Value $result.region 
$item | Add-Member -type NoteProperty -Name  'city' -Value $result.city 
$item | Add-Member -type NoteProperty -Name  'ISP' -Value $result.ISP
$item | Add-Member -type NoteProperty -Name  'ASN' -Value $result.ASN
$item | Add-Member -type NoteProperty -Name  'organization' -Value $result.organization 
$item | Add-Member -type NoteProperty -Name  'latitude' -Value $result.latitude
$item | Add-Member -type NoteProperty -Name  'longitude' -Value $result.longitude
$item | Add-Member -type NoteProperty -Name  'is_crawler' -Value $result.is_crawler
$item | Add-Member -type NoteProperty -Name  'timezone' -Value $result.timezone
$item | Add-Member -type NoteProperty -Name  'mobile' -Value $result.mobile
$item | Add-Member -type NoteProperty -Name  'host' -Value $result.thehost 
$item | Add-Member -type NoteProperty -Name  'proxy' -Value $result.proxy
$item | Add-Member -type NoteProperty -Name  'vpn' -Value $result.vpn
$item | Add-Member -type NoteProperty -Name  'tor' -Value $result.tor
$item | Add-Member -type NoteProperty -Name  'active_vpn' -Value $result.active_vpn
$item | Add-Member -type NoteProperty -Name  'active_tor' -Value $result.active_tor
$item | Add-Member -type NoteProperty -Name  'recent_abuse' -Value $result.recent_abuse
$item | Add-Member -type NoteProperty -Name  'bot_status' -Value $result.bot_status
$Datas += $item

$cpt++
$percent=$cpt/$numberofline*100
Write-Progress -Activity "Search in Progress" -Status "$percent% Complete:" -PercentComplete $percent;

}

$DatasToExport=$Datas | select-object ip,fraudscore,success,message,country_code,region,city,ISP, ASN,organization,latitude,longitude,is_crawler,timezone,mobile,host,proxy,vpn,tor,active_vpn,active_tor,recent_abuse,bot_status


$DatasToExport | ogv -passthru -title "Preview before export"
$DatasToExport | Export-Csv -Path $exitfile -Delimiter ';' -NoTypeInformation

sleep 1
