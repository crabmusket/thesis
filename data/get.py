from datetime import datetime

i = open('sydney2.tmy', 'r')
t = open('time.txt', 'w')
s = open('insolation.txt', 'w')
a = open('ambient.txt', 'w')
c = open('clouds.txt', 'w')
zero = datetime(1, 1, 1)

for line in i:
    # Time
    month = int(line[0:3])
    day   = int(line[3:5])
    hour  = int(line[5:7]) - 1
    time  = datetime(1, month, day, hour)
    delta = time - zero
    t.write('{}\n'.format(delta.days * 24 * 60 * 60 + delta.seconds))

    # Insolation
    horiz  = int(line[7:10]) / float(100)
    direct = int(line[10:13]) / float(100)
    s.write('{}\t{}\n'.format(horiz, direct))

    # Ambient
    ambient = int(line[13:16])
    a.write('{}\n'.format(ambient / float(10)))

    # Wet bulb temp
    bulb = line[19:22]

    # Wind
    windSpeed = line[16:19]
    windDir   = line[22:24]

    # Cloud cover
    clouds = int(line[24])
    c.write('{}\n'.format(clouds))

for f in [i, t, s, a, c]:
    f.close()
