//y = a + bx.

/*Aici, a este intercepția, iar b este panta dreptei. Pentru a calcula panta,
 se folosește formula: b = (nΣ(xy) - ΣxΣy) / (nΣ(x^2) - (Σx)^2),
 a = (Σy - bΣx) / n.
 */

import org.graalvm.polyglot.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.util.Scanner;
import javax.imageio.ImageIO;

public class LinearRegressionApp{

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        System.out.print("Nume imagine (ex: plot.png): ");
        String numeFisier = sc.nextLine();

        System.out.print("Cale salvare (ex: . pentru folder curent): ");
        String cale = sc.nextLine();

        // VECTOR DE CULORI
        String[] culori = {"RED", "BLUE", "GREEN", "BLACK", "ORANGE", "MAGENTA", "CYAN"};

        System.out.println("Alege culoarea pentru puncte:");
        for (int i = 0; i < culori.length; i++) {
            System.out.println(i + " - " + culori[i]);
        }
        int pozPuncte = sc.nextInt();

        System.out.println("Alege culoarea pentru linie:");
        for (int i = 0; i < culori.length; i++) {
            System.out.println(i + " - " + culori[i]);
        }
        int pozLinie = sc.nextInt();

        // ---------- CITIRE DATE DIN PYTHON ----------
        double[] x = new double[100];
        double[] y = new double[100];
        int n = 0;

        try (Context context = Context.newBuilder().allowAllAccess(true).build()) {
            // cod Python pentru citirea fisierului dataset.txt
            String pyScript = """
                    data = []
                    with open('dataset.txt','r') as f:
                        for line in f:
                            parts = line.strip().split() #strip taie spațiile goale de la început și sfârșit.taie spațiile goale de la început și sfârșit.
                            data.append( (float(parts[0]), float(parts[1])) )
                    data #ce returnam""";

            Value result = context.eval("python", pyScript);

            n = (int) result.getArraySize();
            for (int i = 0; i < n; i++) {
                Value point = result.getArrayElement(i);
                x[i] = point.getArrayElement(0).asDouble();
                y[i] = point.getArrayElement(1).asDouble();
            }
        } catch (Exception e) {
            System.out.println("Eroare la citire Python!");
            return;
        }

        // CALCUL REGRESIE
        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;

        for (int i = 0; i < n; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
        }

        double a = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        double b = (sumY - a * sumX) / n;

        System.out.println("Ecuația: y = " + a + "x + " + b);


        // CONVERSIE STRING -> COLOR
        Color culoarePuncte = Color.RED;
        Color culoareLinie = Color.BLUE;

        if (culori[pozPuncte].equals("RED")) culoarePuncte = Color.RED;
        if (culori[pozPuncte].equals("BLUE")) culoarePuncte = Color.BLUE;
        if (culori[pozPuncte].equals("GREEN")) culoarePuncte = Color.GREEN;
        if (culori[pozPuncte].equals("BLACK")) culoarePuncte = Color.BLACK;
        if (culori[pozPuncte].equals("ORANGE")) culoarePuncte = Color.ORANGE;
        if (culori[pozPuncte].equals("MAGENTA")) culoarePuncte = Color.MAGENTA;
        if (culori[pozPuncte].equals("CYAN")) culoarePuncte = Color.CYAN;

        if (culori[pozLinie].equals("RED")) culoareLinie = Color.RED;
        if (culori[pozLinie].equals("BLUE")) culoareLinie = Color.BLUE;
        if (culori[pozLinie].equals("GREEN")) culoareLinie = Color.GREEN;
        if (culori[pozLinie].equals("BLACK")) culoareLinie = Color.BLACK;
        if (culori[pozLinie].equals("ORANGE")) culoareLinie = Color.ORANGE;
        if (culori[pozLinie].equals("MAGENTA")) culoareLinie = Color.MAGENTA;
        if (culori[pozLinie].equals("CYAN")) culoareLinie = Color.CYAN;

        // GENERARE IMAGINE
        try {
            BufferedImage img = new BufferedImage(400, 400, BufferedImage.TYPE_INT_RGB);
            Graphics g = img.getGraphics();

            // desen puncte
            g.setColor(culoarePuncte);
            for (int i = 0; i < n; i++) {
                g.fillOval((int)x[i], 400 - (int)y[i], 5, 5);
            }

            // desen linie regresie
            g.setColor(culoareLinie);
            int x1 = 0;
            int y1 = (int)(a * x1 + b);
            int x2 = 400;
            int y2 = (int)(a * x2 + b);

            g.drawLine(x1, 400 - y1, x2, 400 - y2);

            String fisierFinal = cale + "/" + numeFisier;
            ImageIO.write(img, "png", new File(fisierFinal));

        } catch (Exception e) {
            System.out.println("Eroare la imagine!");
        }
    }
}
