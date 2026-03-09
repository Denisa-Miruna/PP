import java.io.File
fun adaugaCuvant(dictionar: HashMap<String, String>,engl: String, ro: String)
{
    dictionar.put(engl,ro)
}
fun salveazaPoveste(text: String, numeFisier: String)
{
    File(numeFisier).writeText(text)
}
fun citesteDictionar(numeFisier: String): HashMap<String, String>
{
    val dictionar=hashMapOf<String,String>()
    File(numeFisier).forEachLine {
        linie->
        val cuvinte=linie.split("=")
        if(cuvinte.size == 2)
        {
            val engl=cuvinte[0].trim()
            val ro=cuvinte[1].trim()
            dictionar.put(engl,ro)
        }

    }
    return dictionar
}
fun main(args : Array<String>){
    val Dictionar= citesteDictionar("cuvinteDictionar")
    adaugaCuvant(Dictionar, "people", "oameni")
    adaugaCuvant(Dictionar,"were","au fost")
    val Poveste = "Once upon a time there was an old woman who loved baking gingerbread. She would bake gingerbread cookies, cakes, houses and gingerbread people, all decorated with chocolate and peppermint, caramel candies and colored ingredients."
    val words1 = Poveste.split(" ")
    println("Cuvintele din poveste [${words1.count()}]:")
    for (word in words1)
        print(word + " ")
    val words2 = mutableListOf<String>()
    for (word in words1){
        words2.add(word.trim(',','.'))
    }
    println("\n")
    val povesteTradusa= StringBuilder()
    println("Povestea tradusa ar suna cam asa:")
    for (item in words2){
        val translated=Dictionar[item] ?: "[$item]"
        print(translated)
        povesteTradusa.append(translated).append(" ")
        print(" ")
    }
    salveazaPoveste(povesteTradusa.toString(), "PovesteTradusa.txt")
}

