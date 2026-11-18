https://gisportal.comune.milano.it/server/rest/services/D_Mobilita/ATM_Metro/MapServer/0/query?where=&text=&objectIds=&time=&timeRelation=esriTimeRelationOverlaps&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&distance=&units=esriSRUnit_Foot&relationParam=&outFields=linee%2Cnome&returnGeometry=true&returnTrueCurves=false&maxAllowableOffset=&geometryPrecision=&outSR=&havingClause=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&historicMoment=&returnDistinctValues=false&resultOffset=&resultRecordCount=&returnExtentOnly=false&sqlFormat=none&datumTransformation=&parameterValues=&rangeValues=&quantizationParameters=&uniqueIds=&returnUniqueIdsOnly=false&featureEncoding=esriDefault&f=html




https://giromilano.atm.it/proxy.search/api/atmSearch/search?Lang=it&RighePerCategoria=8&Tipi=INDIRIZZO,LOCALITA,POI&page=1&rows=15&soloGeocodificati=true&searchTerm=porta

https://giromilano.atm.it/proxy.tpportal/api/tpPortal/tpl/trips?FromPoint.X=9.190929153680905&FromPoint.Y=45.47986233671701&ToPoint.X=9.187683205036514&ToPoint.Y=45.484926370404594&Date=2026-11-14&FromSeconds=42060&TransportModes=Metro,Bus,Tram,Rail&Lang=it&FromDescription=Stazione centrale, Milano&ToDescription=MILANO PORTA GARIBALDI, Milano

curl 'https://giromilano.atm.it/proxy.tpportal/api/tpPortal/tpl/trips?FromPoint.X=9.190929153680905&FromPoint.Y=45.47986233671701&ToPoint.X=9.187683205036514&ToPoint.Y=45.484926370404594&Date=2026-11-14&FromSeconds=42060&TransportModes=Metro,Bus,Tram,Rail&Lang=it&FromDescription=Bastioni%20di%20Porta%20Nuova,%20%20Milano&ToDescription=MILANO%20PORTA%20GARIBALDI,%20Milano' \
  --compressed \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:159.0) Gecko/20100101 Firefox/159.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'tracestate: eeaf823-c59310fd@dtr=2;07acff75421ab02d;1;55a23a6474838c57;17946528690685366QGB3D1HERQNT8IM3VLNQVDOIDP3P;HUDWUFKMBKFMMNWIHUWKWCFNHKJMJPPU-0;1' \
  -H 'traceparent: 00-97be72bf4de9848152a3693e53df1bae-07acff75421ab02d-01' \
  -H 'x-dtpc: 8$52869063_794h50vKEJQIUHMFLVLCACFFVWBLUTHNBRCMFPI-0e0' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://giromilano.atm.it/' \
  -H 'Cookie: dtCookie9205gfup=v_4_srv_8_sn_4BDC9607D39FF9087612292615BE393E_perc_100000_ol_0_mul_1_app-3A55a23a6474838c57_0_rcs-3Acss_0; TS01ac3475=0199b2c74a16d1911c2ab6916fccd4d0759931c77b3fd41870a2b111a3b467aade7fadff10ab758185e767d3c5f2d8cef901cf80ff6f94fb2bb0e78b8d648deccf40794f8c' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  -H 'TE: trailers'

# linea M1
curl 'https://giromilano.atm.it/proxy.tpportal/api/tpportal/tpl/journeyPatterns/-1|0?alternativeRoutesMode=false' \
  --compressed \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:159.0) Gecko/20100101 Firefox/159.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'tracestate: eeaf823-c59310fd@dtr=2;cf7db5356a8ceb00;1;55a23a6474838c57;1794775886443RJ5RSM297RKG5KKRE306DA2K7DGODV08;RRHFLKRFEDNIBWPFWAFRCSKUWDUUAHUV-0;1' \
  -H 'traceparent: 00-b134e699b5ac3644bfa9dc976c614eaf-cf7db5356a8ceb00-01' \
  -H 'x-dtpc: 8$175886439_806h37vAMUAAULHDNWUKMTVQKRJWMSKRILQLSNP-0e0' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://giromilano.atm.it/' \
  -H 'Cookie: dtCookie9205gfup=v_4_srv_8_sn_4BDC9607D39FF9087612292615BE393E_perc_100000_ol_0_mul_1_app-3A55a23a6474838c57_0_rcs-3Acss_0; TS01ac3475=0199b2c74a5998ff2c18ade1d085da66b7b70ee2ec649c6f126b406316faf362bf90accb656b8bb258f83839b222aa6711dcb4e71bcd7e55ec0351f0d7bcc9cf79efc9f4c6' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  -H 'TE: trailers'

# Tram 


curl 'https://giromilano.atm.it/proxy.tpportal/api/tpportal/tpl/journeyPatterns/1|0?alternativeRoutesMode=false' \
  --compressed \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:159.0) Gecko/20100101 Firefox/159.0' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate, br, zstd' \
  -H 'tracestate: eeaf823-c59310fd@dtr=2;8fc69ef21f9ce0da;1;55a23a6474838c57;1794775886443RJ5RSM297RKG5KKRE306DA2K7DGODV08;HFCWPVUHRMOLQBRTHTRCNJHMOHEMMODN-0;1' \
  -H 'traceparent: 00-b710838caa307bb978eefd68d1941541-8fc69ef21f9ce0da-01' \
  -H 'x-dtpc: 8$175886439_806h65vKHCLHTFAURPEOAORPQUQQIAFHBRQPGSQ-0e0' \
  -H 'Connection: keep-alive' \
  -H 'Referer: https://giromilano.atm.it/' \
  -H 'Cookie: dtCookie9205gfup=v_4_srv_8_sn_4BDC9607D39FF9087612292615BE393E_perc_100000_ol_0_mul_1_app-3A55a23a6474838c57_0_rcs-3Acss_0; TS01ac3475=0199b2c74a54c192170c40cc08aeb9564a58214e71b70aaa8655729d3f99484af7f2c4a6f28f453322082fe566602f6498f281ae42b0439b1bf09c67dfb373a433aa6f4b2e' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Priority: u=0' \
  -H 'TE: trailers'

