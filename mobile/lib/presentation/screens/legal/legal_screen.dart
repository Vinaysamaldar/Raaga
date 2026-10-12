import 'package:flutter/material.dart';
import '../../../core/theme/raaga_theme.dart';

class LegalAndLicensingScreen extends StatefulWidget {
  const LegalAndLicensingScreen({super.key});

  @override
  State<LegalAndLicensingScreen> createState() =>
      _LegalAndLicensingScreenState();
}

class _LegalAndLicensingScreenState extends State<LegalAndLicensingScreen> {
  final _workTitleController = TextEditingController();
  final _claimantController = TextEditingController();
  bool _submitted = false;

  static const List<Map<String, String>> _licensedPartners = [
    {
      'label': 'Anand Audio (ಆನಂದ್ ಆಡಿಯೋ)',
      'agreement': 'Master & Publishing License #KA-ANA-2026-01',
      'royaltyModel': 'Per-Stream Pro-Rata + Offline Cache Accounting',
    },
    {
      'label': 'Lahari Music (ಲಹರಿ ಮ್ಯೂಸಿಕ್)',
      'agreement': 'Master & Publishing License #KA-LAH-2026-02',
      'royaltyModel': 'Per-Stream Pro-Rata + IPRS Mechanical Sync',
    },
    {
      'label': 'Saregama India (ಸರೆಗಮ ಕನ್ನಡ)',
      'agreement': 'Evergreen Classics & Bhavageethe License #KA-SAR-2026-03',
      'royaltyModel': 'Per-Stream Tiered Ledger Reporting',
    },
    {
      'label': 'Aditya Music & PRK Audio',
      'agreement': 'Sandalwood & Indie Catalog License #KA-PRK-2026-04',
      'royaltyModel': 'Automated Monthly ISRC Royalty Settlement',
    },
    {
      'label': 'Jhankar Music (ಝಂಕಾರ್ ಮ್ಯೂಸಿಕ್)',
      'agreement': 'Janapada & Devotional Catalog License #KA-JHA-2026-05',
      'royaltyModel': 'Per-Stream & Offline Play Count Ledger',
    },
  ];

  @override
  void dispose() {
    _workTitleController.dispose();
    _claimantController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Licensing, Legal & Copyright Takedown'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            '1. Licensed Kannada Labels & Royalty Reporting',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: RaagaColors.mysoreGold,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'Raaga streams exclusively rights-cleared Kannada audio under active licensing agreements. Every online stream (>=30 seconds) and offline encrypted play is logged with ISRC codes for automated monthly royalty reporting.',
          ),
          const SizedBox(height: 10),
          ..._licensedPartners.map(
            (p) => Card(
              margin: const EdgeInsets.symmetric(vertical: 4),
              child: ListTile(
                leading: const Icon(Icons.verified, color: RaagaColors.mysoreGold),
                title: Text(p['label']!,
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text('${p['agreement']}\n${p['royaltyModel']}'),
              ),
            ),
          ),
          const Divider(height: 28),
          const Text(
            '2. Terms of Service & Exclusive Kannada Content Policy',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: RaagaColors.mysoreGold,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            '• Content Restriction: Only Kannada-language tracks (language = "Kannada") are permitted on Raaga.\n'
            '• DRM & Offline Encryption: Offline downloads are encrypted using AES-256-CBC with hardware-backed keys and are playable solely inside the Raaga application. Extracting or redistributing audio files is strictly prohibited.',
          ),
          const Divider(height: 28),
          const Text(
            '3. Privacy Policy (DPDP Act 2023 Compliant)',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: RaagaColors.mysoreGold,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            '• We collect only phone number/email for authentication and cross-device sync of Favorites, Playlists, and Listening History.\n'
            '• Voice search audio is processed ephemerally for Kannada/English speech-to-text and is never sold to third parties.',
          ),
          const Divider(height: 28),
          const Text(
            '4. Copyright Takedown Notice (DMCA / Indian Copyright Act 1957)',
            style: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.bold,
              color: RaagaColors.mysoreGold,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _workTitleController,
            decoration: const InputDecoration(
              labelText: 'Track Title / ISRC Code Claimed',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          TextField(
            controller: _claimantController,
            decoration: const InputDecoration(
              labelText: 'Rights Holder / Label Name & Official Email',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 10),
          ElevatedButton.icon(
            onPressed: () => setState(() => _submitted = true),
            icon: const Icon(Icons.gavel),
            label: const Text('Submit Copyright Takedown Request'),
          ),
          if (_submitted)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text(
                'Takedown ticket logged (#TD-KA-2026). Track will be reviewed and quarantined within 24 hours.',
                style: TextStyle(color: RaagaColors.mysoreGold),
              ),
            ),
        ],
      ),
    );
  }
}
