class Wishlist {
  final int id;
  final int userId;
  final String name;

  Wishlist({
    required this.id,
    required this.userId,
    required this.name,
  });

  factory Wishlist.fromJson(Map<String, dynamic> json) {
    return Wishlist(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      name: json['name'] as String,
    );
  }
}
