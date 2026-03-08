class Birth(val year: Int, val Month: Int, val Day: Int){
    override fun toString() : String{
        return "($Day.$Month.$year)"
    }
}
class Contact(val Name: String, val Phone: String, val BirthDate: Birth){
    fun Print() {
        println("Name: $Name, Mobile: $Phone, Date: $BirthDate")
    }
}
// Căutare după nume
fun searchByName(agenda: List<Contact>, name: String): Contact? {
    return agenda.find { it.Name == name }
}

// Căutare după telefon
fun searchByPhone(agenda: List<Contact>, phone: String): Contact? {
    return agenda.find { it.Phone == phone }
}
fun main(args : Array<String>){
    val agenda = mutableListOf<Contact>()
    agenda.add(Contact("Mihai", "0744321987", Birth(1900, 11, 25)))
    agenda += Contact("George", "0761332100", Birth(2002, 3, 14))
    agenda += Contact("Liviu" , "0231450211", Birth(1999, 7, 30))
    agenda += Contact("Popescu", "0211342787", Birth(1955, 5, 12))
    for (persoana in agenda){
        persoana.Print()
    }
    println("Agenda dupa eliminare contact [George]:")
    agenda.removeAt(1)
    for (persoana in agenda){
        persoana.Print()
    }
    agenda.remove(Contact("Liviu" , "0231450211", Birth(1999, 7, 30)))
    //nu va sterge pt ca nu e data class e doar class si verifica doar referintele
    println("Agenda dupa eliminare contact [Liviu]:")
    agenda.removeAt(1)
    for (persoana in agenda){
        persoana.Print()
    }
    // Test căutare după nume
    println("\nCautare dupa nume [George]:")
    val gasit1 = searchByName(agenda, "George")
    gasit1?.Print() ?: println("Contact inexistent")

    // Test căutare după telefon
    println("\nCautare dupa telefon [0211342787]:")
    val gasit2 = searchByPhone(agenda, "0211342787")
    gasit2?.Print() ?: println("Contact inexistent")
}