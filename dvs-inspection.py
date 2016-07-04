import xml.etree.cElementTree as ET
import isodate
import datetime
import logging
import sys

__logger__ = logging.getLogger(__name__)

def get_dvs_details(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exception:
        __logger__.error("Kan XML niet parsen: %s", exception)
        return None

    # Zoek belangrijke nodes op:
    product = root.find('{urn:ndov:cdm:trein:reisinformatie:data:4}ReisInformatieProductDVS')
    namespace = "urn:ndov:cdm:trein:reisinformatie:data:4"

    if product is None:
        # Probeer oude namespace (DVS-TIBCO):
        product = root.find('{urn:ndov:cdm:trein:reisinformatie:data:2}ReisInformatieProductDVS')
        namespace = "urn:ndov:cdm:trein:reisinformatie:data:2"

    administratie = product.find('{%s}RIPAdministratie' % namespace)
    vertrekstaat = product.find('{%s}DynamischeVertrekStaat' % namespace)
    rit_id = vertrekstaat.find('{%s}RitId' % namespace).text
    rit_station = vertrekstaat.find('{%s}RitStation' % namespace).find('{%s}StationCode' % namespace).text
    trein_node = vertrekstaat.find('{%s}Trein' % namespace)

    administratie_volgnummer = administratie.find('{%s}ReisInformatieProductID' % namespace).text
    administratie_abo = administratie.find('{%s}AbonnementId' % namespace).text
    administratie_tijdstip = administratie.find('{%s}ReisInformatieTijdstip' % namespace).text
    timestamp = product.attrib.get('TimeStamp')
    vertrektijd = trein_node.find('{%s}VertrekTijd' % namespace).text
    vertraging = iso_duur_naar_seconden(trein_node.find('{%s}ExacteVertrekVertraging' % namespace).text)
    status = trein_node.find('{%s}TreinStatus' % namespace).text

    vertrek_dt = isodate.parse_datetime(vertrektijd)
    timestamp_dt = isodate.parse_datetime(timestamp)

    verschil_ontvangst_vertrek = vertrek_dt - timestamp_dt

    return administratie_abo, administratie_volgnummer, timestamp_dt, administratie_tijdstip, rit_id, rit_station, vertrek_dt, vertraging, status, verschil_ontvangst_vertrek.total_seconds()

def iso_duur_naar_seconden(string):
    if len(string) > 0:
        if string[0] == '-':
            return isodate.parse_duration(string[1:]).seconds * -1

    return isodate.parse_duration(string).seconds

def get_iso_date_string(string):
    idate = isodate.parse_datetime(string)
    return idate.date

window = 70

marge_min = window * 60 - 30
marge_max = window * 60 + 30

first_seen = {}
first_timestamp = None
timestamp_dt_th = None

window_delta = datetime.timedelta(minutes=window)

counter_total = {}
counter_service = {}
counter_late = {}

with open(sys.argv[1], 'r') as f:
    for line in f:
        dvs_details = get_dvs_details(line)

        if dvs_details[0] == "0":
            # Negeer PPV bijmenging voor nu
            continue
        
        if first_timestamp is None:
            first_timestamp = dvs_details[2]
            timestamp_th = first_timestamp + window_delta
        
        vertrekdatum = dvs_details[6].strftime('%Y-%m-%d')
        rit_stat_id = dvs_details[5] + "_" + dvs_details[4] + "_" + vertrekdatum

        if vertrekdatum in counter_total:
            counter_total[vertrekdatum] += 1
        else:
            counter_total[vertrekdatum] = 1
            counter_late[vertrekdatum] = 0
            counter_service[vertrekdatum] = 0

        # Check whether exists:
        if rit_stat_id in first_seen:
            continue
        else:
            # Add 
            first_seen[rit_stat_id] = dvs_details[9]
            counter_service[vertrekdatum] += 1

            if dvs_details[2] < timestamp_th:
                # Don't care over te late meldingen
                # Valt nog binnen opstarttijd
                continue

            if dvs_details[9] < marge_min or dvs_details[9] > marge_max:
                # Eerste bericht voor deze rit buiten marge
                # Bereken gewenste tijdstip voor verzenden bericht (ahdv vertrektijd)
                eigenlijke_timestamp = dvs_details[6] - window_delta
                print vertrekdatum, eigenlijke_timestamp.strftime("%H:%M:%S"), dvs_details[4], dvs_details[5], rit_stat_id, dvs_details[9]
                counter_late[vertrekdatum] += 1

print
print "Stats"
print "====="

for datum in counter_total:
    print "%s: Totaal %s berichten. %s ritten, %s te laat = %0.2f procent" % (datum, counter_total[datum], counter_service[datum], counter_late[datum], (float(counter_late[datum])/counter_service[datum])*100)
