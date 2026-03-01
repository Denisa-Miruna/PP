package org.example;
import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.Value;
import java.util.Set;
public class Main {
    public static void main(String[] args) {
        try (Context context = Context.newBuilder().allowAllAccess(true).build()) {
            Set<String> languages = context.getEngine().getLanguages().keySet();
            for (String id : languages) {
                System.out.println("Initializing language " + id);
                context.initialize(id);
                switch (id) {
                    case "python":
                        context.eval("python", "print('Hello Python!')");
                        break;
                    case "js":
                        context.eval("js", "print('Hello JavaScript!');");
                        break;
                    case "ruby":
                        context.eval("ruby", "puts 'Hello Ruby!'");
                        break;
                    case "java":
                        Value out = context.getBindings("java").getMember("java.lang.System").getMember("out");
                        out.invokeMember("println", "Hello Espresso Java!");
                        break;
                }
            }
        }
    }
}