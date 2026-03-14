package org.webcrawler

import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import org.jsoup.Jsoup
import org.jsoup.nodes.Element
import org.jsoup.parser.Parser as JsoupParser
import org.yaml.snakeyaml.LoaderOptions
import org.yaml.snakeyaml.Yaml
import org.yaml.snakeyaml.constructor.SafeConstructor


//  INTERFATA Parser

interface Parser {
    fun parse(text: String): Map<String, Any>
}

//  Exemple de input:
//    {"name": "Ana", "age": 20}   →  {"name"="Ana", "age"=20.0}
//    [1, 2, 3]                    →  {"items"=[1, 2, 3]}
//
class JsonParser : Parser {

    private val gson = Gson()

    override fun parse(text: String): Map<String, Any> {
        require(text.isNotBlank()) { "Textul JSON este gol!" }

        val textCurat = text.trim()

        return if (textCurat.startsWith("{")) {
            // JSON obiect  →  deserializam direct in Map
            val tip = object : TypeToken<Map<String, Any>>() {}.type
            gson.fromJson(textCurat, tip)

        } else if (textCurat.startsWith("[")) {
            // JSON array  →  impachetam intr-un Map cu cheia "items"
            val tip = object : TypeToken<List<Any>>() {}.type
            val lista: List<Any> = gson.fromJson(textCurat, tip)
            mapOf("items" to lista)

        } else {
            throw IllegalArgumentException("Textul nu este JSON valid!")
        }
    }
}


//  XmlParser
//  Exemplu de input:
//    <nota><catre>Ana</catre></nota>  →  {"nota"={"catre"="Ana"}}
//
class XmlParser : Parser {

    override fun parse(text: String): Map<String, Any> {
        require(text.isNotBlank()) { "Textul XML este gol!" }

        // Parsam documentul cu Jsoup in modul XML (nu HTML)
        val document = Jsoup.parse(text, "", JsoupParser.xmlParser())

        // Luam elementul radacina (primul element din document)
        val radacina = document.children().firstOrNull()
            ?: return emptyMap()

        return mapOf(radacina.tagName() to elementToMap(radacina))
    }

    // Functie recursiva: converteste un Element Jsoup in Map sau String
    @Suppress("UNCHECKED_CAST")
    private fun elementToMap(element: Element): Any {
        val rezultat = mutableMapOf<String, Any>()

        // Salvam atributele elementului (ex: <book id="1"> → "@atribute"={"id"="1"})
        if (element.attributes().size() > 0) {
            rezultat["@atribute"] = element.attributes().associate { it.key to it.value }
        }

        val copii = element.children()

        return if (copii.isEmpty()) {
            // Element frunza (fara copii) → returnam textul sau map-ul cu atribute
            val text = element.text().trim()
            if (rezultat.isEmpty()) text else rezultat.also { it["#text"] = text }

        } else {
            // Element cu copii → procesam recursiv fiecare copil
            for (copil in copii) {
                val tag = copil.tagName()
                val valoare = elementToMap(copil)

                if (rezultat.containsKey(tag)) {
                    // Tag duplicat → grupam intr-o lista
                    val existent = rezultat[tag]
                    if (existent is MutableList<*>) {
                        (existent as MutableList<Any>).add(valoare)
                    } else {
                        rezultat[tag] = mutableListOf(existent!!, valoare)
                    }
                } else {
                    rezultat[tag] = valoare
                }
            }
            rezultat
        }
    }
}


//  YamlParser

//  Exemplu de input:
//    name: Ana       →  {"name"="Ana"}
//    age: 20
//
class YamlParser : Parser {

    private val yaml = Yaml(SafeConstructor(LoaderOptions()))

    @Suppress("UNCHECKED_CAST")
    override fun parse(text: String): Map<String, Any> {
        require(text.isNotBlank()) { "Textul YAML este gol!" }

        return when (val rezultat: Any? = yaml.load(text)) {
            is Map<*, *>  -> rezultat as Map<String, Any>   // YAML obiect → Map direct
            is List<*>    -> mapOf("items" to rezultat)     // YAML lista  → impacheat
            else          -> mapOf("valoare" to (rezultat ?: ""))
        }
    }
}


//  Crawler

class Crawler(private val url: String) {

    // Asociem fiecare Content-Type cu parserul corespunzator
    private val parseri: Map<String, Parser> = mapOf(
        "application/json"   to JsonParser(),
        "text/json"          to JsonParser(),
        "application/xml"    to XmlParser(),
        "text/xml"           to XmlParser(),
        "application/x-yaml" to YamlParser(),
        "text/yaml"          to YamlParser(),
        "text/x-yaml"        to YamlParser()
    )

    /*
     * Trimite o cerere HTTP GET si returneaza raspunsul Jsoup.
     * .ignoreContentType(true) = accepta orice tip, nu doar HTML
     */
    fun getResource(): org.jsoup.Connection.Response {
        println("  → Se descarca: $url")

        return try {
            val raspuns = Jsoup.connect(url)
                .header("Accept", "application/json, application/xml, text/yaml, */*")
                .userAgent("KotlinWebCrawler/1.0")
                .ignoreContentType(true)
                .ignoreHttpErrors(true)
                .timeout(30_000)
                .execute()

            println("  → Status: ${raspuns.statusCode()} | Content-Type: ${raspuns.contentType()}")
            raspuns

        } catch (e: Exception) {
            throw RuntimeException("Nu s-a putut accesa '$url': ${e.message}")
        }
    }

    /*Primeste Content-Type, alege parserul si parseaza corpul raspunsului.
     */
    fun processContent(contentType: String): Map<String, Any>? {
        val tipMedia = contentType.split(";").first().trim().lowercase()
        println("  → Tip detectat: $tipMedia")

        val parser = parseri[tipMedia] ?: run {
            println("  → ATENTIE: Niciun parser pentru '$tipMedia'")
            return null
        }

        println("  → Parser: ${parser::class.simpleName}")
        val raspuns = getResource()
        return parser.parse(raspuns.body())
    }

    fun crawl(): Map<String, Any>? {
        val raspuns = getResource()
        val contentType = raspuns.contentType() ?: "application/octet-stream"
        return processContent(contentType)
    }
}


fun main() {

    // --- TEST 1: JsonParser fara HTTP ---
    println("[1] JsonParser (date locale)")
    val jsonText = """{"id": 1, "titlu": "Kotlin", "activ": true}"""
    val jsonRezultat = JsonParser().parse(jsonText)
    afiseaza(jsonRezultat)

    println()

    // --- TEST 2: XmlParser fara HTTP ---
    println("[2] XmlParser (date locale)")
    val xmlText = """
        <nota>
            <catre>Ana</catre>
            <de_la>Ion</de_la>
            <mesaj>Salut!</mesaj>
        </nota>
    """.trimIndent()
    val xmlRezultat = XmlParser().parse(xmlText)
    afiseaza(xmlRezultat)

    println()

    // --- TEST 3: YamlParser fara HTTP ---
    println("[3] YamlParser (date locale)")
    val yamlText = """
        server:
          host: localhost
          port: 8080
        features:
          - json
          - xml
          - yaml
    """.trimIndent()
    val yamlRezultat = YamlParser().parse(yamlText)
    afiseaza(yamlRezultat)

    println()

    // --- TEST 4: Crawler complet cu HTTP real ---
    println("[4] Crawler HTTP - JSON (jsonplaceholder.typicode.com)")
    try {
        val rezultat = Crawler("https://jsonplaceholder.typicode.com/todos/1").crawl()
        if (rezultat != null) afiseaza(rezultat)
    } catch (e: Exception) {
        println("  → Eroare (verifica conexiunea): ${e.message}")
    }

    println()

    println("[5] Crawler HTTP - XML (w3schools.com)")
    try {
        val rezultat = Crawler("https://www.w3schools.com/xml/note.xml").crawl()
        if (rezultat != null) afiseaza(rezultat)
    } catch (e: Exception) {
        println("  → Eroare (verifica conexiunea): ${e.message}")
    }

}

@Suppress("UNCHECKED_CAST")
fun afiseaza(map: Map<String, Any>, indent: String = "  ") {
    for ((cheie, valoare) in map) {
        if (valoare is Map<*, *>) {
            println("$indent$cheie:")
            afiseaza(valoare as Map<String, Any>, "$indent  ")
        } else {
            println("$indent$cheie = $valoare")
        }
    }
}