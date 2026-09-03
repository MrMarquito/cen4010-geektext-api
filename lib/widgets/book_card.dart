import 'package:flutter/material.dart';
import '../models/book.dart';
import 'book_cover.dart';

class InteractiveBookCard extends StatefulWidget {
  final Book book;
  final VoidCallback onTap;
  final VoidCallback onAddToCart;

  const InteractiveBookCard({
    super.key,
    required this.book,
    required this.onTap,
    required this.onAddToCart,
  });

  @override
  State<InteractiveBookCard> createState() => _InteractiveBookCardState();
}

class _InteractiveBookCardState extends State<InteractiveBookCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOutCubic,
          transform: Matrix4.identity()..translate(0.0, _isHovered ? -6.0 : 0.0),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: _isHovered ? Colors.indigo.shade200 : const Color(0xFFF1F5F9),
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: _isHovered
                    ? Colors.indigo.withOpacity(0.12)
                    : Colors.black.withOpacity(0.04),
                blurRadius: _isHovered ? 20 : 8,
                offset: Offset(0, _isHovered ? 12 : 4),
              ),
            ],
          ),
          padding: const EdgeInsets.all(14.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Stylized Cover
              Expanded(
                child: Center(
                  child: BookCover(
                    title: widget.book.name,
                    genre: widget.book.genre,
                    publisher: widget.book.publisher,
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Title and Meta
              Text(
                widget.book.name,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0F172A),
                  height: 1.2,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 2),
              Text(
                '${widget.book.copiesSold} copies sold • ${widget.book.yearPublished}',
                style: TextStyle(fontSize: 11, color: Colors.grey.shade600),
              ),
              const SizedBox(height: 8),

              // Price and Action Footer
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '\$${widget.book.price.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 17,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF047857),
                    ),
                  ),
                  InkWell(
                    onTap: widget.onAddToCart,
                    borderRadius: BorderRadius.circular(10),
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.indigo.shade50,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.add_shopping_cart_rounded,
                        size: 18,
                        color: Colors.indigo.shade700,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
