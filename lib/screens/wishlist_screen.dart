import 'package:flutter/material.dart';
import '../models/book.dart';
import '../models/wishlist.dart';
import '../services/api_service.dart';

class WishlistScreen extends StatefulWidget {
  final int userId;

  const WishlistScreen({super.key, this.userId = 1});

  @override
  State<WishlistScreen> createState() => _WishlistScreenState();
}

class _WishlistScreenState extends State<WishlistScreen> {
  final ApiService _apiService = ApiService();
  List<Wishlist> _wishlists = [];
  Wishlist? _selectedWishlist;
  List<Book> _books = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadWishlists();
  }

  Future<void> _loadWishlists() async {
    setState(() => _isLoading = true);
    try {
      final lists = await _apiService.getUserWishlists(widget.userId);
      setState(() {
        _wishlists = lists;
        if (_wishlists.isNotEmpty) {
          _selectedWishlist = _wishlists.first;
        } else {
          _selectedWishlist = null;
          _books = [];
        }
      });
      if (_selectedWishlist != null) {
        await _loadBooksForWishlist(_selectedWishlist!.id);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading wishlists: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _loadBooksForWishlist(int wishlistId) async {
    setState(() => _isLoading = true);
    try {
      final books = await _apiService.getWishlistBooks(wishlistId);
      setState(() => _books = books);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading books: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _showCreateWishlistDialog() async {
    final controller = TextEditingController();
    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Create New Wishlist'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Wishlist Name',
            hintText: 'e.g. Summer Reading',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final name = controller.text.trim();
              if (name.isEmpty) return;
              Navigator.pop(ctx);
              try {
                await _apiService.createWishlist(widget.userId, name);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Created wishlist "$name"')),
                  );
                }
                await _loadWishlists();
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red),
                  );
                }
              }
            },
            child: const Text('Create'),
          ),
        ],
      ),
    );
  }

  Future<void> _moveToCart(String isbn, String bookName) async {
    if (_selectedWishlist == null) return;
    try {
      await _apiService.moveWishlistBookToCart(_selectedWishlist!.id, isbn);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Moved "$bookName" to shopping cart!')),
        );
      }
      await _loadBooksForWishlist(_selectedWishlist!.id);
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
      appBar: AppBar(
        title: const Text('Wish Lists'),
        actions: [
          IconButton(
            tooltip: 'Create Wishlist',
            icon: const Icon(Icons.add),
            onPressed: _wishlists.length >= 3 ? null : _showCreateWishlistDialog,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Wishlist Selector Header
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (_wishlists.isNotEmpty)
                        DropdownButton<Wishlist>(
                          value: _selectedWishlist,
                          items: _wishlists.map((w) {
                            return DropdownMenuItem(value: w, child: Text(w.name));
                          }).toList(),
                          onChanged: (Wishlist? selected) {
                            if (selected != null) {
                              setState(() => _selectedWishlist = selected);
                              _loadBooksForWishlist(selected.id);
                            }
                          },
                        )
                      else
                        const Text(
                          'No wishlists yet (Maximum: 3)',
                          style: TextStyle(fontSize: 16, color: Colors.grey),
                        ),
                      Text(
                        '${_wishlists.length} / 3 Lists',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const Divider(height: 24),

                  // Books in Active Wishlist
                  Expanded(
                    child: _selectedWishlist == null
                        ? Center(
                            child: ElevatedButton.icon(
                              icon: const Icon(Icons.add),
                              label: const Text('Create your first Wishlist'),
                              onPressed: _showCreateWishlistDialog,
                            ),
                          )
                        : _books.isEmpty
                            ? const Center(child: Text('This wishlist is empty.'))
                            : ListView.separated(
                                itemCount: _books.length,
                                separatorBuilder: (_, __) => const Divider(),
                                itemBuilder: (context, index) {
                                  final book = _books[index];
                                  return ListTile(
                                    leading: const Icon(Icons.bookmark_outline, size: 36),
                                    title: Text(book.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                                    subtitle: Text(
                                      '${book.genre} • \$${book.price.toStringAsFixed(2)}',
                                    ),
                                    trailing: ElevatedButton.icon(
                                      icon: const Icon(Icons.shopping_cart_checkout, size: 18),
                                      label: const Text('Move to Cart'),
                                      onPressed: () => _moveToCart(book.isbn, book.name),
                                    ),
                                  );
                                },
                              ),
                  ),
                ],
              ),
            ),
    );
  }
}
