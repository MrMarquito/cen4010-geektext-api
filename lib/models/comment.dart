class BookComment {
  final int id;
  final int userId;
  final String bookIsbn;
  final String comment;
  final String createdAt;

  BookComment({
    required this.id,
    required this.userId,
    required this.bookIsbn,
    required this.comment,
    required this.createdAt,
  });

  factory BookComment.fromJson(Map<String, dynamic> json) {
    return BookComment(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      bookIsbn: json['book_isbn'] as String,
      comment: json['comment'] as String,
      createdAt: json['created_at'] as String,
    );
  }
}
