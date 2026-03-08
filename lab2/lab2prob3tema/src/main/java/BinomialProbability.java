import org.graalvm.polyglot.*;
import java.util.Scanner;

public class BinomialProbability {

    // Funcție pentru combinări nCk
    static long comb(int n, int k) {
        if (k > n) return 0;
        if (k == 0 || k == n) return 1;
        long res = 1;
        for (int i = 1; i <= k; i++) {
            res = res * (n - i + 1) / i;
        }
        return res;
    }

    // Probabilitate cumulativa binomiala P(X <= x)
    static double binomialCDF(int n, int x, double p) {
        double sum = 0.0;
        for (int k = 0; k <= x; k++) {
            long C = comb(n, k);
            sum += C * Math.pow(p, k) * Math.pow(1 - p, n - k);
        }
        return sum;
    }

    public static void main(String[] args) {
        // Creăm context Polyglot care permite acces la Python
        try (Context context = Context.newBuilder().allowAllAccess(true).build()) {

            // Citire n și x din Python
            String pythonCode = """
            n = int(input("Introduceti numarul de aruncari (n): "))
            x = int(input("Introduceti numarul x (1 <= x <= n): "))
            [n, x]  # Returnam ca lista
            """;

            Value result = context.eval("python", pythonCode);
            int n = result.getArrayElement(0).asInt();
            int x = result.getArrayElement(1).asInt();

            if (x < 1 || x > n) {
                System.out.println("x trebuie sa fie intre 1 si n!");
                return;
            }

            double p = 0.5; // probabilitatea pajurii
            double prob = binomialCDF(n, x, p);

            System.out.printf("Probabilitatea de a obtine cel mult %d pajuri din %d aruncari: %.5f%n", x, n, prob);
        }
    }
}