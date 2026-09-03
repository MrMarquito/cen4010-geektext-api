class UserProfile {
  final int id;
  final String username;
  final String? name;
  final String? email;
  final String? address;

  UserProfile({
    required this.id,
    required this.username,
    this.name,
    this.email,
    this.address,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as int,
      username: json['username'] as String,
      name: json['name'] as String?,
      email: json['email'] as String?,
      address: json['address'] as String?,
    );
  }
}
