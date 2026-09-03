class Book {
  final String isbn;
  final int authorId;
  final String name;
  final String? description;
  final double price;
  final String genre;
  final String publisher;
  final int yearPublished;
  final int copiesSold;

  Book({
    required this.isbn,
    required this.authorId,
    required this.name,
    this.description,
    required this.price,
    required this.genre,
    required this.publisher,
    required this.yearPublished,
    required this.copiesSold,
  });

  factory Book.fromJson(Map<String, dynamic> json) {
    return Book(
      isbn: json['isbn'] as String,
      authorId: json['author_id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      price: (json['price'] as num).toDouble(),
      genre: json['genre'] as String,
      publisher: json['publisher'] as String,
      yearPublished: json['year_published'] as int,
      copiesSold: json['copies_sold'] as int? ?? 0,
    );
  }
}
