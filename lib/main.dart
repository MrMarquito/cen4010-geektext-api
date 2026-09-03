import 'package:flutter/material.dart';
import 'models/book.dart';
import 'services/api_service.dart';
import 'screens/cart_screen.dart';
import 'screens/book_details_screen.dart';
import 'screens/wishlist_screen.dart';
import 'screens/profile_screen.dart';
import 'widgets/book_card.dart';

void main() {
  runApp(const GeekTextApp());
}

class GeekTextApp extends StatelessWidget {
  const GeekTextApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GeekText Bookstore',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1E1B4B),
          primary: const Color(0xFF1E1B4B),
          secondary: const Color(0xFF047857),
        ),
      ),
      home: const BookListScreen(),
    );
  }
}

class BookListScreen extends StatefulWidget {
  const BookListScreen({super.key});

  @override
  State<BookListScreen> createState() => _BookListScreenState();
}

class _BookListScreenState extends State<BookListScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<Book>> _booksFuture;
  String _activeFilter = 'Top Sellers';

  final List<String> _genres = const [
    'Top Sellers',
    'Technology',
    'Sci-Fi',
    'Fantasy',
    'Fiction'
  ];

  @override
  void initState() {
    super.initState();
    _booksFuture = _initializeAndLoad();
  }

  Future<List<Book>> _initializeAndLoad() async {
    final activeUrl = await _apiService.discoverActiveBackend();
    if (mounted) {
      if (activeUrl != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Connected to: $activeUrl'),
            duration: const Duration(seconds: 2),
            backgroundColor: const Color(0xFF0F172A),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No active backend reached. Configure server via the link icon.'),
            backgroundColor: Colors.amber,
          ),
        );
      }
    }
    return _apiService.getTopSellers();
  }

  void _onFilterSelected(String genre) {
    setState(() {
      _activeFilter = genre;
      if (genre == 'Top Sellers') {
        _booksFuture = _apiService.getTopSellers();
      } else {
        _booksFuture = _apiService.getBooksByGenre(genre);
      }
    });
  }

  void _showDiscountDialog() {
    final pubController = TextEditingController();
    final discController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Apply Publisher Discount'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: pubController,
              decoration: const InputDecoration(
                labelText: 'Publisher Name',
                hintText: 'e.g. Prentice Hall',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: discController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Discount Percent',
                hintText: 'e.g. 15',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final pub = pubController.text.trim();
              final disc = double.tryParse(discController.text.trim());
              if (pub.isEmpty || disc == null) return;

              Navigator.pop(ctx);
              try {
                await _apiService.applyPublisherDiscount(pub, disc);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Applied $disc% discount to $pub')),
                  );
                }
                _onFilterSelected(_activeFilter);
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                  );
                }
              }
            },
            child: const Text('Apply'),
          ),
        ],
      ),
    );
  }

  void _showServerSettings() {
    final controller = TextEditingController(text: ApiService.baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Backend Configuration'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Active Tunnel URL',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              final url = controller.text.trim();
              if (url.isNotEmpty) {
                _apiService.setBaseUrl(url);
                Navigator.pop(ctx);
                _onFilterSelected(_activeFilter);
              }
            },
            child: const Text('Save & Reconnect'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF1E1B4B),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.auto_stories, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Text(
              'GeekText',
              style: TextStyle(
                fontWeight: FontWeight.w800,
                color: Color(0xFF0F172A),
                letterSpacing: -0.5,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'Server Settings',
            icon: const Icon(Icons.hub_outlined, color: Color(0xFF475569)),
            onPressed: _showServerSettings,
          ),
          IconButton(
            tooltip: 'Apply Publisher Discount',
            icon: const Icon(Icons.percent_rounded, color: Color(0xFF475569)),
            onPressed: _showDiscountDialog,
          ),
          IconButton(
            tooltip: 'Wishlists',
            icon: const Icon(Icons.bookmarks_outlined, color: Color(0xFF475569)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const WishlistScreen(userId: 1)),
              );
            },
          ),
          IconButton(
            tooltip: 'Shopping Cart',
            icon: const Icon(Icons.shopping_bag_outlined, color: Color(0xFF475569)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const CartScreen(userId: 1)),
              );
            },
          ),
          IconButton(
            tooltip: 'Profile',
            icon: const Icon(Icons.person_outline_rounded, color: Color(0xFF475569)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const ProfileScreen(defaultUsername: 'testuser'),
                ),
              );
            },
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // Hero Banner
          SliverToBoxAdapter(
            child: Container(
              margin: const EdgeInsets.all(20),
              padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 32),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                gradient: const LinearGradient(
                  colors: [Color(0xFF0F172A), Color(0xFF1E1B4B)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.amber.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Text(
                            'CURATED SOFTWARE ARCHITECTURE & FICTION',
                            style: TextStyle(
                              color: Colors.amber,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1.2,
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Level Up Your Library.',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 28,
                            fontWeight: FontWeight.w800,
                            letterSpacing: -0.5,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          'Explore industry classics, clean architectures, and speculative horizons.',
                          style: TextStyle(
                            color: const Color(0xFFCBD5E1),
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Filter Chips Section
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: _genres.map((genre) {
                    final isSelected = _activeFilter == genre;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: FilterChip(
                        label: Text(genre),
                        selected: isSelected,
                        onSelected: (_) => _onFilterSelected(genre),
                        selectedColor: const Color(0xFF1E1B4B),
                        backgroundColor: Colors.white,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : const Color(0xFF334155),
                          fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                          fontSize: 13,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                          side: BorderSide(
                            color: isSelected ? Colors.transparent : Colors.grey.shade200,
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ),

          // Books Catalog Grid
          SliverPadding(
            padding: const EdgeInsets.all(20),
            sliver: FutureBuilder<List<Book>>(
              future: _booksFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const SliverFillRemaining(
                    child: Center(child: CircularProgressIndicator()),
                  );
                } else if (snapshot.hasError) {
                  return SliverFillRemaining(
                    child: Center(
                      child: Text(
                        'Failed to reach backend: ${snapshot.error}',
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  );
                } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return const SliverFillRemaining(
                    child: Center(child: Text('No books found for this category.')),
                  );
                }

                final books = snapshot.data!;
                return SliverLayoutBuilder(
                  builder: (context, constraints) {
                    int crossAxisCount = constraints.crossAxisExtent > 1100
                        ? 4
                        : (constraints.crossAxisExtent > 750 ? 3 : (constraints.crossAxisExtent > 500 ? 2 : 1));

                    return SliverGrid(
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: crossAxisCount,
                        crossAxisSpacing: 18,
                        mainAxisSpacing: 18,
                        childAspectRatio: 0.72,
                      ),
                      delegate: SliverChildBuilderDelegate(
                        (context, index) {
                          final book = books[index];
                          return InteractiveBookCard(
                            book: book,
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (_) => BookDetailsScreen(book: book, userId: 1),
                                ),
                              );
                            },
                            onAddToCart: () async {
                              try {
                                await _apiService.addToCart(1, book.isbn);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Added "${book.name}" to cart'),
                                      duration: const Duration(seconds: 1),
                                    ),
                                  );
                                }
                              } catch (e) {
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
                                  );
                                }
                              }
                            },
                          );
                        },
                        childCount: books.length,
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
