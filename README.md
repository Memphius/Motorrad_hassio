# BMW Motorrad ConnectedRide for Home Assistant

Custom Home Assistant integratie voor BMW Motorrad ConnectedRide.

## Wat doet deze integratie

Deze integratie haalt motorfietsgegevens op uit de BMW Motorrad cloud en maakt daarvan Home Assistant-entiteiten aan, zoals:

- brandstofniveau
- resterende actieradius
- kilometerstand
- trip 1
- bandenspanning voor en achter
- volgende service datum
- afstand tot service
- laatste bekende locatie
- laatste verbindings- en activatiemoment

De integratie is read-only. Er worden geen opdrachten naar BMW of de motor gestuurd.

## Hoe werkt de authenticatie

De integratie gebruikt de BMW CarData device-code flow:

1. je vult in Home Assistant je BMW CarData client-ID in
2. Home Assistant vraagt een device code op bij BMW
3. je opent de BMW verificatielink
4. je keurt het apparaat goed met de getoonde code
5. Home Assistant wisselt daarna de device code om voor een token
6. met dat token worden de Motorrad-gegevens opgehaald

## Vereisten

- Home Assistant
- HACS of handmatige installatie
- een BMW CarData client-ID uit het BMW CarData portaal
> Zie hier https://www.bmw-motorrad.nl/nl/my-bmw-motorrad-vm4/my-garage.html#/my-bike/ 
- een BMW Motorrad account met ConnectedRide / clouddata

## Installatie via HACS

1. voeg deze repository toe als custom repository in HACS
2. kies type: Integration
3. installeer de integratie
4. herstart Home Assistant

## Handmatige installatie

Kopieer deze map naar:

/config/custom_components/bmw_motorrad_connectedride

Herstart daarna Home Assistant.

## Configuratie

Voeg de integratie toe via:

Instellingen → Apparaten en diensten → Integratie toevoegen

Vul daarna in:

- **Client ID**: je BMW CarData client-ID
- **Landcode**: bijvoorbeeld `nl-NL`
- **Motorrad API-host**: standaard `https://cpp.bmw-motorrad.com`
- **BMW CarData auth-host**: standaard `https://customer.bmwgroup.com`
- **Poll-interval**: bijvoorbeeld `300`
- **SSL verifiëren**: aan laten staan

## Wat er technisch gebeurt

De integratie vraagt data op uit de BMW Motorrad API en zet deze om naar Home Assistant entities. Sommige waarden uit BMW worden omgerekend naar bruikbare eenheden, bijvoorbeeld:

- afstanden naar km
- kilometerstanden naar km
- bandenspanning naar bar
- timestamps naar datum/tijd

## Bekende punten

- de integratie is afhankelijk van BMW cloudservices
- als BMW endpoints of authenticatie wijzigt, kan de integratie tijdelijk stoppen met werken
- de integratie is op dit moment alleen read-only
- sommige BMW velden kunnen per model of regio verschillen

## Problemen oplossen

### Geen data / onbekende waarden
- controleer of de integratie correct is geautoriseerd
- controleer of de motor in de BMW app zichtbaar is
- herlaad of herstart Home Assistant

### Token- of autorisatiefout
- verwijder de integratie
- voeg hem opnieuw toe
- doorloop de device-code flow opnieuw

### Logs bekijken
Ga naar:

Instellingen → Systeem → Logboeken

Zoek op:

`bmw_motorrad_connectedride`

## Entiteiten opnieuw opbouwen

Als je oude of fout benoemde entiteiten wilt opruimen:

1. verwijder de integratie
2. herstart Home Assistant
3. voeg de integratie opnieuw toe

Dat is de schoonste manier om entitynamen en devices opnieuw op te bouwen.

## Disclaimer

Dit project is niet officieel gelieerd aan BMW of BMW Motorrad.
Gebruik op eigen risico.
