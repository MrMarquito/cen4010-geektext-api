import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/book.dart';
import '../models/comment.dart';
import '../models/wishlist.dart';
import '../models/user_profile.dart';

class ApiService {
  // Singleton pattern so the selected URL stays consistent across screens
    static final ApiService _instance = ApiService._internal();
    factory ApiService() => _instance;
    ApiService._internal();

    // Known candidate URLs (Add your desktop tunnel, laptop tunnel, and localhost)
    static final List<String> candidateUrls = [
      'https://syndrome-bigger-semester-los.trycloudflare.com', // Active tunnel
      'https://your-laptop-url.trycloudflare.com',              // Other machine tunnel
      'http://localhost:8000',                                  // Local fallback
    ];

    static String baseUrl = candidateUrls.first;

    // Checks each URL with a 3-second timeout and binds the first active one
    Future<String?> discoverActiveBackend() async {
      for (final url in candidateUrls) {
        try {
          final response = await http
              .get(Uri.parse('$url/'))
              .timeout(const Duration(seconds: 3));

          if (response.statusCode == 200) {
            baseUrl = url;
            return url;
          }
        } catch (_) {
          // Machine offline or tunnel down; try next candidate
          continue;
        }
      }
      return null;
    }

    // Method to allow manually pasting a new tunnel URL at runtime
    void setBaseUrl(String newUrl) {
      baseUrl = newUrl.endsWith('/') ? newUrl.substring(0, newUrl.length - 1) : newUrl;
    }

  // Retrieve Top 10 sellers
  Future<List<Book>> getTopSellers() async {
    final response = await http.get(Uri.parse('$baseUrl/books/top-sellers'));

    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((dynamic item) => Book.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load top sellers');
    }
  }

  // Retrieve books filtered by genre
  Future<List<Book>> getBooksByGenre(String genre) async {
    final response = await http.get(Uri.parse('$baseUrl/books/genre/$genre'));

    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((dynamic item) => Book.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load books by genre');
    }
  }

  // Retrieve a single book by ISBN
  Future<Book> getBookByIsbn(String isbn) async {
    final response = await http.get(Uri.parse('$baseUrl/books/$isbn'));

    if (response.statusCode == 200) {
      return Book.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Book not found');
    }
  }

  // Feature 1: Discount books by publisher
    Future<void> applyPublisherDiscount(String publisher, double discountPercent) async {
      final response = await http.put(
        Uri.parse('$baseUrl/books/discount'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'publisher': publisher,
          'discount_percent': discountPercent,
        }),
      );

      if (response.statusCode != 200) {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to apply discount');
      }
    }


  // Feature 2: Retrieve user by username
    Future<UserProfile> getUser(String username) async {
      final response = await http.get(Uri.parse('$baseUrl/users/$username'));
      if (response.statusCode == 200) {
        return UserProfile.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('User not found');
      }
    }

    // Feature 2: Update user fields (excluding email)
    Future<void> updateUser(String username, {String? name, String? password, String? address}) async {
      final Map<String, dynamic> body = {};
      if (name != null && name.isNotEmpty) body['name'] = name;
      if (password != null && password.isNotEmpty) body['password'] = password;
      if (address != null && address.isNotEmpty) body['address'] = address;

      final response = await http.put(
        Uri.parse('$baseUrl/users/$username'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );

      if (response.statusCode != 200) {
        throw Exception('Failed to update profile');
      }
    }

    // Feature 2: Link a credit card to a user
    Future<void> addCreditCard(String username, String cardNumber, String expiration, String cvv) async {
      final response = await http.post(
        Uri.parse('$baseUrl/users/$username/credit-cards'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'card_number': cardNumber,
          'expiration': expiration,
          'cvv': cvv,
        }),
      );

      if (response.statusCode != 201) {
        throw Exception('Failed to add credit card');
      }
    }


  // Feature 3: Add book to shopping cart
  Future<void> addToCart(int userId, String isbn) async {
    final response = await http.post(
      Uri.parse('$baseUrl/cart/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'book_isbn': isbn}),
    );

    if (response.statusCode != 201) {
      throw Exception('Failed to add book to cart');
    }
  }

  // Feature 3: Retrieve books in shopping cart
  Future<List<Book>> getCartBooks(int userId) async {
    final response = await http.get(Uri.parse('$baseUrl/cart/$userId'));

    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((item) => Book.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load cart items');
    }
  }

  // Feature 3: Retrieve cart subtotal
  Future<double> getCartSubtotal(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/cart/$userId/subtotal'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['subtotal'] as num).toDouble();
    } else {
      throw Exception('Failed to load subtotal');
    }
  }

  // Feature 3: Delete a book from cart
  Future<void> removeFromCart(int userId, String isbn) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/cart/$userId/books/$isbn'),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to remove book from cart');
    }
  }

  // Feature 5: Get average rating for a book
  Future<double> getAverageRating(String isbn) async {
    final response = await http.get(
      Uri.parse('$baseUrl/books/$isbn/rating/average'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['average_rating'] as num).toDouble();
    } else {
      throw Exception('Failed to load average rating');
    }
  }

  // Feature 5: Get all comments for a book
  Future<List<BookComment>> getBookComments(String isbn) async {
    final response = await http.get(Uri.parse('$baseUrl/books/$isbn/comments'));
    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((item) => BookComment.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load comments');
    }
  }

  // Feature 5: Add a rating (1-5 stars)
  Future<void> addRating(int userId, String isbn, int rating) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ratings/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'book_isbn': isbn,
        'rating': rating,
      }),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to submit rating');
    }
  }

  // Feature 5: Add a comment
  Future<void> addComment(int userId, String isbn, String comment) async {
    final response = await http.post(
      Uri.parse('$baseUrl/comments/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'book_isbn': isbn,
        'comment': comment,
      }),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to post comment');
    }
  }

  // Feature 6: Get all wishlists for a user
  Future<List<Wishlist>> getUserWishlists(int userId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/users/$userId/wishlists'),
    );
    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((item) => Wishlist.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load wishlists');
    }
  }

  // Feature 6: Create a new wishlist (enforces 3-list cap on backend)
  Future<void> createWishlist(int userId, String name) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wishlists/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'name': name}),
    );
    if (response.statusCode != 201) {
      final error = jsonDecode(response.body);
      throw Exception(error['detail'] ?? 'Failed to create wishlist');
    }
  }

  // Feature 6: Add a book to a wishlist
  Future<void> addToWishlist(int wishlistId, String isbn) async {
    final response = await http.post(
      Uri.parse('$baseUrl/wishlists/items'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'wishlist_id': wishlistId, 'book_isbn': isbn}),
    );
    if (response.statusCode != 201) {
      throw Exception('Failed to add book to wishlist');
    }
  }

  // Feature 6: List books in a wishlist
  Future<List<Book>> getWishlistBooks(int wishlistId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/wishlists/$wishlistId/books'),
    );
    if (response.statusCode == 200) {
      final List<dynamic> body = jsonDecode(response.body);
      return body.map((item) => Book.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load wishlist books');
    }
  }

  // Feature 6: Remove book from wishlist into the shopping cart
  Future<void> moveWishlistBookToCart(int wishlistId, String isbn) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/wishlists/$wishlistId/books/$isbn'),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to transfer book to cart');
    }
  }
}
