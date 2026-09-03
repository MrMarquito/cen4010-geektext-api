import 'package:flutter/material.dart';
import '../models/user_profile.dart';
import '../services/api_service.dart';

class ProfileScreen extends StatefulWidget {
  final String defaultUsername;

  const ProfileScreen({super.key, this.defaultUsername = 'testuser'});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ApiService _apiService = ApiService();

  final _lookupController = TextEditingController();
  final _nameController = TextEditingController();
  final _addressController = TextEditingController();
  final _passwordController = TextEditingController();

  final _cardNumberController = TextEditingController();
  final _expirationController = TextEditingController();
  final _cvvController = TextEditingController();

  UserProfile? _currentUser;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _lookupController.text = widget.defaultUsername;
    _fetchProfile(widget.defaultUsername);
  }

  Future<void> _fetchProfile(String username) async {
    if (username.trim().isEmpty) return;
    setState(() => _isLoading = true);
    try {
      final user = await _apiService.getUser(username.trim());
      setState(() {
        _currentUser = user;
        _nameController.text = user.name ?? '';
        _addressController.text = user.address ?? '';
        _passwordController.clear();
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _updateProfile() async {
    if (_currentUser == null) return;
    try {
      await _apiService.updateUser(
        _currentUser!.username,
        name: _nameController.text.trim(),
        address: _addressController.text.trim(),
        password: _passwordController.text.trim(),
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Profile updated successfully!')),
        );
      }
      _fetchProfile(_currentUser!.username);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _addCard() async {
    if (_currentUser == null) return;
    try {
      await _apiService.addCreditCard(
        _currentUser!.username,
        _cardNumberController.text.trim(),
        _expirationController.text.trim(),
        _cvvController.text.trim(),
      );
      _cardNumberController.clear();
      _expirationController.clear();
      _cvvController.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Credit card linked successfully!')),
        );
      }
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
      appBar: AppBar(title: const Text('Profile Management')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Lookup Bar
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _lookupController,
                          decoration: const InputDecoration(
                            labelText: 'Lookup by Username',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      ElevatedButton(
                        onPressed: () => _fetchProfile(_lookupController.text),
                        child: const Text('Load'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  if (_currentUser != null) ...[
                    // Update Profile Card
                    Card(
                      elevation: 2,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Edit Profile Details', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 12),
                            TextField(
                              controller: TextEditingController(text: _currentUser!.email ?? 'None'),
                              readOnly: true,
                              enabled: false,
                              decoration: const InputDecoration(
                                labelText: 'Email (Read-only / Cannot be modified)',
                                border: OutlineInputBorder(),
                                filled: true,
                              ),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _nameController,
                              decoration: const InputDecoration(labelText: 'Full Name', border: OutlineInputBorder()),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _addressController,
                              decoration: const InputDecoration(labelText: 'Home Address', border: OutlineInputBorder()),
                            ),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _passwordController,
                              obscureText: true,
                              decoration: const InputDecoration(
                                labelText: 'New Password (leave empty to keep current)',
                                border: OutlineInputBorder(),
                              ),
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _updateProfile,
                              child: const Text('Save Profile Changes'),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Add Credit Card Card
                    Card(
                      elevation: 2,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Add Credit Card', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 12),
                            TextField(
                              controller: _cardNumberController,
                              decoration: const InputDecoration(labelText: 'Card Number', border: OutlineInputBorder()),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _expirationController,
                                    decoration: const InputDecoration(labelText: 'Expiration (MM/YY)', border: OutlineInputBorder()),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(
                                  child: TextField(
                                    controller: _cvvController,
                                    decoration: const InputDecoration(labelText: 'CVV', border: OutlineInputBorder()),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _addCard,
                              child: const Text('Link Credit Card'),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
}
