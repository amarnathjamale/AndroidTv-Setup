package com.gathin.tvhome;

/**
 * The Marathi (amanta, Shalivahana Shaka) calendar date, e.g. "आश्विन कृष्ण दशमी · शके १९४८", shown in the lunar_date
 * line when the launcher speaks Marathi. No network and no ICU: the Sun and Moon come from Jean Meeus' "Astronomical
 * Algorithms" (Sun ch. 25, Moon ch. 47 truncated to its larger terms, about 0.01 degree), sidereal by the Lahiri
 * ayanamsa.
 *
 * Conventions, as a Maharashtrian panchang prints them:
 * - The tithi is the one running at sunrise in Pune, so a day keeps one tithi even when the TV is abroad.
 * - Months are amanta (new moon to new moon) and take their name from the sidereal sign the Sun is in at the new moon
 *   that starts them (Sun in Meena: Chaitra). A month whose two new moons share a sign is adhik (intercalary).
 * - The Shaka year is the Gregorian year minus 78 from Chaitra (Gudi Padwa) and minus 79 before it.
 */
final class Panchang {

    private Panchang() {
    }

    private static final double PUNE_LAT = 18.52;
    private static final double PUNE_LON = 73.86;

    static final String[] MONTHS = {"चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद", "आश्विन",
            "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"};
    static final String[] TITHIS = {"प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी",
            "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी"};

    /** Today's date in the Marathi calendar, for the date the TV shows (its own time zone), reckoned at Pune's sunrise. */
    static String today() {
        long now = System.currentTimeMillis();
        long localDay = Math.floorDiv(now + java.util.TimeZone.getDefault().getOffset(now), 86_400_000L);
        return format(localDay);
    }

    /** {tithi 1..30, month 0..11 (Chaitra = 0), adhik 0/1, shaka year} for a day counted from 1970-01-01 (IST). */
    static int[] compute(long epochDay) {
        double jd0 = 2440587.5 + epochDay;                    // 00:00 UT of that date
        double jdRise = jd0 + sunriseUtcHours(jd0) / 24.0;
        double e = elongation(jdRise);
        int tithi = (int) Math.floor(e / 12.0) + 1;
        double nm = newMoonBefore(jdRise);
        int sign = siderealSign(nm);
        int month = Math.floorMod(sign + 1, 12);
        int nextSign = siderealSign(newMoonBefore(nm + 35));
        int adhik = nextSign == sign ? 1 : 0;
        int[] g = gregorian(epochDay);
        int shaka = g[0] - 78;
        if (g[1] <= 4 && month >= 9) shaka = g[0] - 79;     // Pausha, Magha, Phalguna early in the year
        return new int[]{tithi, month, adhik, shaka};
    }

    static String format(long epochDay) {
        int[] p = compute(epochDay);
        int t = p[0];
        String paksha = t <= 15 ? "शुक्ल" : "कृष्ण";
        String tithi;
        if (t == 15) tithi = "पौर्णिमा";
        else if (t == 30) tithi = "अमावास्या";
        else tithi = TITHIS[(t - 1) % 15];
        String month = (p[2] == 1 ? "अधिक " : "") + MONTHS[p[1]];
        return month + " " + paksha + " " + tithi + " · शके " + devanagari(p[3]);
    }

    static String devanagari(int n) {
        String s = Integer.toString(n);
        StringBuilder b = new StringBuilder();
        for (char c : s.toCharArray()) b.append(c >= '0' && c <= '9' ? (char) ('०' + (c - '0')) : c);
        return b.toString();
    }

    // ---- astronomy -----------------------------------------------------------------------------------

    private static double norm(double a) {
        a %= 360.0;
        return a < 0 ? a + 360.0 : a;
    }

    private static double sin(double deg) {
        return Math.sin(Math.toRadians(deg));
    }

    /** Apparent tropical longitude of the Sun (Meeus 25), degrees. */
    static double sunLongitude(double jd) {
        double t = (jd - 2451545.0) / 36525.0;
        double l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t;
        double m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t;
        double c = (1.914602 - 0.004817 * t - 0.000014 * t * t) * sin(m)
                + (0.019993 - 0.000101 * t) * sin(2 * m) + 0.000289 * sin(3 * m);
        double omega = 125.04 - 1934.136 * t;
        return norm(l0 + c - 0.00569 - 0.00478 * sin(omega));
    }

    // Meeus table 47.A, longitude terms with |coefficient| >= 0.002 degree: D, M, M', F, coefficient (1e-6 degree).
    private static final int[][] MOON = {
            {0, 0, 1, 0, 6288774}, {2, 0, -1, 0, 1274027}, {2, 0, 0, 0, 658314}, {0, 0, 2, 0, 213618},
            {0, 1, 0, 0, -185116}, {0, 0, 0, 2, -114332}, {2, 0, -2, 0, 58793}, {2, -1, -1, 0, 57066},
            {2, 0, 1, 0, 53322}, {2, -1, 0, 0, 45758}, {0, 1, -1, 0, -40923}, {1, 0, 0, 0, -34720},
            {0, 1, 1, 0, -30383}, {2, 0, 0, -2, 15327}, {0, 0, 1, 2, -12528}, {0, 0, 1, -2, 10980},
            {4, 0, -1, 0, 10675}, {0, 0, 3, 0, 10034}, {4, 0, -2, 0, 8548}, {2, 1, -1, 0, -7888},
            {2, 1, 0, 0, -6766}, {1, 0, -1, 0, -5163}, {1, 1, 0, 0, 4987}, {2, -1, 1, 0, 4036},
            {2, 0, 2, 0, 3994}, {4, 0, 0, 0, 3861}, {2, 0, -3, 0, 3665}, {0, 1, -2, 0, -2689},
            {2, 0, -1, 2, -2602}, {2, -1, -2, 0, 2390}, {1, 0, 1, 0, -2348}, {2, -2, 0, 0, 2236},
            {0, 1, 2, 0, -2120}, {0, 2, 0, 0, -2069},
    };

    /** Apparent tropical longitude of the Moon (Meeus 47, truncated), degrees. */
    static double moonLongitude(double jd) {
        double t = (jd - 2451545.0) / 36525.0;
        double lp = 218.3164477 + 481267.88123421 * t - 0.0015786 * t * t;
        double d = 297.8501921 + 445267.1114034 * t - 0.0018819 * t * t;
        double m = 357.5291092 + 35999.0502909 * t - 0.0001536 * t * t;
        double mp = 134.9633964 + 477198.8675055 * t + 0.0087414 * t * t;
        double f = 93.2720950 + 483202.0175233 * t - 0.0036539 * t * t;
        double e = 1 - 0.002516 * t - 0.0000074 * t * t;
        double sum = 0;
        for (int[] r : MOON) {
            double coef = r[4];
            if (Math.abs(r[1]) == 1) coef *= e;
            else if (Math.abs(r[1]) == 2) coef *= e * e;
            sum += coef * sin(r[0] * d + r[1] * m + r[2] * mp + r[3] * f);
        }
        double a1 = 119.75 + 131.849 * t;
        double a2 = 53.09 + 479264.290 * t;
        sum += 3958 * sin(a1) + 1962 * sin(lp - f) + 318 * sin(a2);
        double omega = 125.04 - 1934.136 * t;
        return norm(lp + sum / 1e6 - 0.00478 * sin(omega));
    }

    /** Moon minus Sun, 0..360. */
    static double elongation(double jd) {
        return norm(moonLongitude(jd) - sunLongitude(jd));
    }

    /** Julian day of the last new moon at or before jd. */
    static double newMoonBefore(double jd) {
        double t = jd - elongation(jd) / 12.1907;
        for (int i = 0; i < 6; i++) {
            double e = elongation(t);
            if (e > 180) e -= 360;
            t -= e / 12.1907;
        }
        if (t > jd + 1e-6) t = newMoonBefore(jd - 29.0);
        return t;
    }

    /** Lahiri ayanamsa, degrees: 23.853 at J2000, precessing 50.29" a year. */
    static double ayanamsa(double jd) {
        return 23.853 + (jd - 2451545.0) / 365.25 * 50.29 / 3600.0;
    }

    static int siderealSign(double jd) {
        return (int) Math.floor(norm(sunLongitude(jd) - ayanamsa(jd)) / 30.0);
    }

    /** Sunrise in Pune, hours after 00:00 UT of the date whose 00:00 UT is jd0 (NOAA's simple algorithm). */
    static double sunriseUtcHours(double jd0) {
        double n = jd0 + 0.5 - 2451545.0;
        double meanAnomaly = norm(357.5291 + 0.98560028 * n);
        double c = 1.9148 * sin(meanAnomaly) + 0.02 * sin(2 * meanAnomaly) + 0.0003 * sin(3 * meanAnomaly);
        double lambda = norm(meanAnomaly + c + 180 + 102.9372);
        double decl = Math.toDegrees(Math.asin(sin(lambda) * sin(23.44)));
        double cosH = (sin(-0.833) - sin(PUNE_LAT) * sin(decl))
                / (Math.cos(Math.toRadians(PUNE_LAT)) * Math.cos(Math.toRadians(decl)));
        double hourAngle = Math.toDegrees(Math.acos(Math.max(-1, Math.min(1, cosH))));
        double doy = (n % 365.2422 + 365.2422) % 365.2422 + 1;                 // n counts from 1 Jan 2000, noon
        double b = 360.0 / 365.0 * (doy - 81);
        double eqTime = (9.87 * sin(2 * b) - 7.53 * Math.cos(Math.toRadians(b)) - 1.5 * sin(b)) / 60.0;  // hours
        double solarNoonUtc = 12 - PUNE_LON / 15.0 - eqTime;
        return solarNoonUtc - hourAngle / 15.0;
    }

    /** {year, month 1..12, day} of a day counted from 1970-01-01. */
    static int[] gregorian(long epochDay) {
        long z = epochDay + 719468;
        long era = Math.floorDiv(z, 146097);
        long doe = z - era * 146097;
        long yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
        long doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
        long mp = (5 * doy + 2) / 153;
        int d = (int) (doy - (153 * mp + 2) / 5 + 1);
        int m = (int) (mp < 10 ? mp + 3 : mp - 9);
        int y = (int) (yoe + era * 400 + (m <= 2 ? 1 : 0));
        return new int[]{y, m, d};
    }
}
