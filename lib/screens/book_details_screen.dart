import 'package:flutter/material.dart';
import '../models/book.dart';
import '../models/comment.dart';
import '../services/api_service.dart';
import '../models/wishlist.dart';

class BookDetailsScreen extends StatefulWidget {
  final Book book;
  final int userId;

  const BookDetailsScreen({super.key, required this.book, this.userId = 1});

  @override
  State<BookDetailsScreen> createState() => _BookDetailsScreenState();
}

class _BookDetailsScreenState extends State<BookDetailsScreen> {
  final ApiService _apiService = ApiService();
  final TextEditingController _commentController = TextEditingController();

  late Future<double> _averageRatingFuture;
  late Future<List<BookComment>> _commentsFuture;
  int _selectedRating = 5;

  @override
  void initState() {
    super.initState();
    _refreshReviews();
  }

  void _refreshReviews() {
    setState(() {
      _averageRatingFuture = _apiService.getAverageRating(widget.book.isbn);
      _commentsFuture = _apiService.getBookComments(widget.book.isbn);
    });
  }

  Future<void> _showAddToWishlistDialog() async {
      try {
        final wishlists = await _apiService.getUserWishlists(widget.userId);
        if (!mounted) return;

        if (wishlists.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('No wishlists found. Create one in the Wishlist screen first!')),
          );
          return;
        }

        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Add to Wishlist'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: wishlists.map((w) {
                return ListTile(
                  leading: const Icon(Icons.bookmark_border),
                  title: Text(w.name),
                  onTap: () async {
                    Navigator.pop(ctx);
                    try {
                      await _apiService.addToWishlist(w.id, widget.book.isbn);
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Added to "${w.name}"')),
                        );
                      }
                    } catch (e) {
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                        );
                      }
                    }
                  },
                );
              }).toList(),
            ),
          ),
        );
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }

  Future<void> _submitRating() async {
    try {
      await _apiService.addRating(
        widget.userId,
        widget.book.isbn,
        _selectedRating,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Submitted $_selectedRating-star rating!')),
        );
      }
      _refreshReviews();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _submitComment() async {
    if (_commentController.text.trim().isEmpty) return;

    try {
      await _apiService.addComment(
        widget.userId,
        widget.book.isbn,
        _commentController.text.trim(),
      );
      _commentController.clear();
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('Comment posted!')));
      }
      _refreshReviews();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.book.name)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Book Information Section
            Card(
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.book.name,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'ISBN: ${widget.book.isbn}',
                      style: const TextStyle(color: Colors.grey),
                    ),
                    Text(
                      'Publisher: ${widget.book.publisher} (${widget.book.yearPublished})',
                    ),
                    Text('Genre: ${widget.book.genre}'),
                    Text('Copies Sold: ${widget.book.copiesSold}'),
                    const SizedBox(height: 12),
                    Text(
                      widget.book.description ?? 'No description provided.',
                      style: const TextStyle(fontSize: 15),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '\$${widget.book.price.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                        Row(
                          children: [
                            ElevatedButton.icon(
                                icon: const Icon(Icons.add_shopping_cart),
                              label: const Text('Add to Cart'),
                              onPressed: () async {
                              try {
                                await _apiService.addToCart(
                                  widget.userId,
                                  widget.book.isbn,
                                );
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        'Added "${widget.book.name}" to cart',
                                      ),
                                    ),
                                  );
                                }
                              } catch (e) {
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Error: $e'),
                                      backgroundColor: Colors.red,
                                    ),
                                  );
                                }
                              }
                            },
                          ),
                          const SizedBox(width: 12),
                              OutlinedButton.icon(
                                icon: const Icon(Icons.bookmark_add_outlined),
                                label: const Text('Add to Wishlist'),
                                onPressed: _showAddToWishlistDialog,
                              ),
                        ]
                      )
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Average Rating Display
            Row(
              children: [
                const Icon(Icons.star, color: Colors.amber, size: 28),
                const SizedBox(width: 8),
                FutureBuilder<double>(
                  future: _averageRatingFuture,
                  builder: (context, snapshot) {
                    final avg = snapshot.data ?? 0.0;
                    return Text(
                      'Average Rating: ${avg.toStringAsFixed(1)} / 5.0',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    );
                  },
                ),
              ],
            ),
            const Divider(height: 32),

            // Submit Rating Control
            Row(
              children: [
                const Text(
                  'Rate this book:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(width: 16),
                DropdownButton<int>(
                  value: _selectedRating,
                  items: [1, 2, 3, 4, 5].map((val) {
                    return DropdownMenuItem(
                      value: val,
                      child: Text('$val Stars'),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedRating = val);
                  },
                ),
                const SizedBox(width: 16),
                ElevatedButton(
                  onPressed: _submitRating,
                  child: const Text('Submit Rating'),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Post Comment Input
            TextField(
              controller: _commentController,
              decoration: InputDecoration(
                labelText: 'Leave a comment',
                border: const OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.send),
                  onPressed: _submitComment,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Comments List Section
            const Text(
              'Customer Comments',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            FutureBuilder<List<BookComment>>(
              future: _commentsFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return const Text('No comments yet. Be the first to review!');
                }

                final comments = snapshot.data!;
                return ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: comments.length,
                  separatorBuilder: (_, __) => const Divider(),
                  itemBuilder: (context, index) {
                    final c = comments[index];
                    return ListTile(
                      leading: const Icon(Icons.person_pin, size: 36),
                      title: Text(c.comment),
                      subtitle: Text(
                        'User #${c.userId} • Posted on ${c.createdAt.split('T').first}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    );
                  },
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
