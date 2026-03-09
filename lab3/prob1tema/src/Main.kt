import org.jsoup.Jsoup

// ADT pentru un item din RSS
data class RSSItem(
    val title: String,
    val link: String,
    val description: String
)

// ADT pentru RSS Feed
data class RSSFeed(
    val title: String,
    val link: String,
    val description: String,
    val items: List<RSSItem>
)

fun main() {
    // URL-ul feedului RSS
    val rssUrl = "http://rss.cnn.com/rss/edition.rss"

    // Conectăm la RSS și obținem documentul HTML/XML
    val doc = Jsoup.connect(rssUrl).get()

    // Extragem <channel> din feed
    val channel = doc.selectFirst("channel")

    // Titlul, linkul și descrierea feedului
    val feedTitle = channel?.selectFirst("title")?.text() ?: "Fara titlu"
    val feedLink = channel?.selectFirst("link")?.text() ?: "Fara link"
    val feedDescription = channel?.selectFirst("description")?.text() ?: ""

    // Extragem toate item-urile
    val itemsList = mutableListOf<RSSItem>()
    if (channel != null) {
        val items = channel.select("item")
        for (item in items) {
            val title = item.selectFirst("title")?.text() ?: "Fara titlu"
            val link = item.selectFirst("link")?.text() ?: "Fara link"
            val description = item.selectFirst("description")?.text() ?: ""
            itemsList.add(RSSItem(title, link, description))
        }
    }

    // Construim feed-ul
    val feed = RSSFeed(feedTitle, feedLink, feedDescription, itemsList)

    // Afisam titlul feedului
    println("Feed: ${feed.title}")
    println("Link feed: ${feed.link}")
    println("Descriere feed: ${feed.description}")
    println("\n--- ITEM-URI ---\n")

    // Afisam fiecare item
    for (item in feed.items) {
        println("Titlu: ${item.title}")
        println("Link: ${item.link}")
        println("Descriere: ${item.description}")
        println("------------------------")
    }
}