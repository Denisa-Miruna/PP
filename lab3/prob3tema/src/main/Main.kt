import org.jsoup.Jsoup
import java.io.File
import java.net.URL

data class Node(
    val url: String,
    val children: MutableList<Node> = mutableListOf()
)

val visited = mutableSetOf<String>()
var linkCount = 0
const val MAX_LINKS = 50

fun getDomain(url: String): String = URL(url).host

// extrage linkuri doar pentru paginile importante
fun extractLinks(url: String, domain: String): List<String> {
    val links = mutableListOf<String>()
    if (linkCount >= MAX_LINKS) return links
    try {
        val doc = Jsoup.connect(url)
            .userAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
            .timeout(15000)
            .get()

        val elements = doc.select("a[href]")

        for (e in elements) {
            val link = e.absUrl("href")
            if (linkCount >= MAX_LINKS) break
            // păstrăm doar linkuri importante (users, tags, questions) și același domeniu
            if (link.startsWith("https://$domain") &&
                (link.contains("/questions") || link.contains("/tags") || link.contains("/users")) &&
                !visited.contains(link)
            ) {
                links.add(link)
                visited.add(link)
                linkCount++
            }
        }

    } catch (e: Exception) {
        println("Nu pot accesa $url")
    }
    return links
}

// construiește arbore recursivitate 2
fun buildTree(url: String, depth: Int, domain: String): Node {
    val node = Node(url)
    if (depth == 0 || linkCount >= MAX_LINKS) return node
    val links = extractLinks(url, domain)
    for (link in links) {
        val child = buildTree(link, depth - 1, domain)
        node.children.add(child)
    }
    return node
}

// afisare arbore
fun printTree(node: Node, level: Int = 0) {
    println("  ".repeat(level) + node.url)
    for (child in node.children) printTree(child, level + 1)
}

// serialize tree in string
fun serializeTree(node: Node): String {
    val childrenSerialized = node.children.joinToString("|") { serializeTree(it) }
    return "${node.url}[$childrenSerialized]"
}

// deserialize tree from string
fun deserializeTree(data: String): Node {
    val url = data.substringBefore("[")
    val inside = data.substringAfter("[").substringBeforeLast("]")
    val node = Node(url)
    if (inside.isNotEmpty()) {
        val children = inside.split("|")
        for (child in children) node.children.add(deserializeTree(child))
    }
    return node
}

// save tree to file
fun saveTreeToFile(tree: Node, filename: String) {
    val serialized = serializeTree(tree)
    File(filename).writeText(serialized)
}

// load tree from file
fun loadTreeFromFile(filename: String): Node {
    val content = File(filename).readText()
    return deserializeTree(content)
}

fun main() {
    val startUrl = "https://stackoverflow.com"
    val domain = getDomain(startUrl)

    val tree = buildTree(startUrl, 2, domain)

    println("ARBORUL:")
    printTree(tree)

    val filename = "stackoverflow_tree.txt"
    saveTreeToFile(tree, filename)
    println("\nArborele a fost salvat în $filename")

    val loadedTree = loadTreeFromFile(filename)
    println("\nARBORUL DESERIALIZAT DIN FISIER:")
    printTree(loadedTree)
}