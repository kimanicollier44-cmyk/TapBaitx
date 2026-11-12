import java.security.MessageDigest;

/**
 * TapBaitx - Java port of the core models (JDK stdlib only, zero deps).
 * Same rules as the Python core: synthetic fixtures only, consent-first.
 * Build/run:  javac TapBaitx.java && java TapBaitx
 * NOTE: authored on a VM with no JDK - source-delivered, compile on a
 * machine with JDK 17+ to run its self-checks.
 */
public class TapBaitx {

    public static String formatNumber(String raw) {
        String d = raw.replaceAll("\\D", "");
        if (d.length() == 11 && d.startsWith("1")) d = d.substring(1);
        if (d.length() != 10) throw new IllegalArgumentException("need a 10-digit US number");
        return "(" + d.substring(0, 3) + ") " + d.substring(3, 6) + "-" + d.substring(6);
    }

    public static boolean isSynthetic(String raw) {
        String d = raw.replaceAll("\\D", "");
        if (d.length() == 11 && d.startsWith("1")) d = d.substring(1);
        return d.substring(3, 6).equals("555");
    }

    public static double[] fuzz(double lat, double lon, int decimals) {
        double f = Math.pow(10, decimals);
        return new double[]{ Math.round(lat * f) / f, Math.round(lon * f) / f };
    }

    public static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
        double R = 6371.0;
        double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
        double dp = Math.toRadians(lat2 - lat1), dl = Math.toRadians(lon2 - lon1);
        double h = Math.pow(Math.sin(dp / 2), 2)
                 + Math.cos(p1) * Math.cos(p2) * Math.pow(Math.sin(dl / 2), 2);
        return 2 * R * Math.asin(Math.sqrt(h));
    }

    public static String detectFormat(byte[] data) {
        if (data.length >= 6 && data[0] == 'G' && data[1] == 'I' && data[2] == 'F') return "image/gif";
        if (data.length >= 3 && (data[0] & 0xFF) == 0xFF && (data[1] & 0xFF) == 0xD8) return "image/jpeg";
        if (data.length >= 8 && data[4] == 'f' && data[5] == 't' && data[6] == 'y' && data[7] == 'p') return "video/mp4";
        if (data.length >= 4 && (data[0] & 0xFF) == 0x89 && data[1] == 'P') return "image/png";
        return "application/octet-stream";
    }

    public static String fingerprint(byte[] data) throws Exception {
        byte[] hash = MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) sb.append(String.format("%02x", b));
        return sb.toString();
    }

    public static int[] tileLayout(int n) {
        if (n <= 0) return new int[]{0, 0};
        int cols = (int) Math.ceil(Math.sqrt(n));
        int rows = (int) Math.ceil((double) n / cols);
        return new int[]{cols, rows};
    }

    public static void main(String[] args) throws Exception {
        int passed = 0, total = 6;
        if (formatNumber("2025550147").equals("(202) 555-0147")) passed++;
        if (isSynthetic("2025550147")) passed++;
        double[] f = fuzz(34.0522, -118.2437, 1);
        if (f[0] == 34.1 && f[1] == -118.2) passed++;
        if (haversineKm(34.05, -118.24, 37.77, -122.42) > 500) passed++;
        if (detectFormat("GIF89a".getBytes()).equals("image/gif")) passed++;
        if (tileLayout(9)[0] == 3) passed++;
        System.out.println("JAVA CHECKS " + passed + "/" + total);
        if (passed != total) System.exit(1);
    }
}
