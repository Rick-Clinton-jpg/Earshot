# System issue — no relay answers produced

These 110 invocation records never produced an answer. Their saved terminal error text reports the Codex account usage limit. Rick identifies this as the account quota shared by the relay calls and the executor. They are system-issue diagnostics, not agent results, gate rejections, or agent failures. The original trace fields remain unchanged as historical records; current summaries use the classification in PATH_MAP.json.

The earliest system-issue record started at 2026-11-06T18:59:17.298991Z (18:59:17 UTC rounded to seconds). Two successful calls in that same concurrent batch started milliseconds later, so the statement that every call after the first system-issue start stopped would be inaccurate. The exceptions are:

- `d1-study-ensure-published-AC-r1`: started 2026-11-06T18:59:17.302182Z; finished 2026-11-06T18:59:33.200680Z.
- `d1-study-ensure-published-AB-r1`: started 2026-11-06T18:59:17.303554Z; finished 2026-11-06T18:59:31.569829Z.

Every saved invocation with a start timestamp later than the last answer-producing call (2026-11-06T18:59:17.303554Z) is a system-issue record. No claim is made that those invocations reached agent execution.

| Path from repository root | SHA-256 |
| --- | --- |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AB-r1.json` | `dad9c53ab410b76589d0123583450ea86cc8afcccc80645fc308e4e40faaf854` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AB-r2.json` | `689bf4bced9a7274aa122b22613098ce5410d9894b78ecceebe27f0f201b8dbf` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AC-r1.json` | `c5d0599ac74d6eb5ca063c2857b5117ebe2e0197e66f90807849b886183403f0` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AC-r2.json` | `f5c1bd7677f39f969a9d6ccf95923aaa9f54ed52cd89147d651b8a4c6f04abe0` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AD-r1.json` | `da200546881db2a80b3fa7f42cfcee9de7ef0d828cbad49eab14c4efaef02cc1` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-AD-r2.json` | `f0369b26984560e817439a47d58529708e87ebb182d81b356af274253c014398` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-BC-r1.json` | `2782c27905c205c666a49dfd651e816f03eedc07a0a203f55864c44e592047c4` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-BC-r2.json` | `cd2c94f38749db2c5e40b4b0ed7ff6ba346f3944332527c2a70b0acdf8ee0bf1` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-BD-r1.json` | `36b94f73602ddc87c30fae82ffaef4cde565ddff158eaa7d8b744ac00ce7dedd` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-BD-r2.json` | `220d262d3819d225dd55d0ec7b8481b9355189c734dc3b738ad74885f01a68f6` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-CD-r1.json` | `7363bd5de3ec26df28d730dd9291d5e191489ba7fda37a61a769e52ba4655d43` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-CD-r2.json` | `aea09c2c9698de3c63c08ae185b23fdb068964209ed5bfac840aa69dc6cdd151` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-free-r1.json` | `a0b84c6dabe93f8513fc864b2aeb06c4e83ef1fd657d920e0ef08dab3f13ea87` |
| `sprint/trial_run/system_issue/d1-heldout-decoded-correct-free-r2.json` | `4601401e43c48ef4e9500b9d9f2dd14499459f4a38f1f8f70c5dcf0da925e3c7` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AB-r1.json` | `a7d4dad8ea1ff31c3621d88f3829312b7a19f288d7c156f140cb82fcabc93fed` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AB-r2.json` | `bf495d0d254bf548a0bf327d2759d33d02fadb4fe8a97b035e5721e9928d6094` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AC-r1.json` | `d2bf3294632c4699690ac59a3caaf24c4617a39d9294c9edf5c9fd798e3f4c4d` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AC-r2.json` | `0e4dcf550d032e444b011f1e745bf1379d430f73d5213745903ace85b6d081fa` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AD-r1.json` | `73a325604ec2312d1a5a3d9821846af3e104212350a2ae335e3ab641b01c4cb0` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-AD-r2.json` | `48f4de7bbc1ec5d7599e1da60fbcdaefe35c97698ad81459d434ec2a725fcc8c` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-BC-r1.json` | `0c00b6a016a4f8ed80a102231c62e47e0d740833e969dd7ffa5d093be480bbda` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-BC-r2.json` | `8fb2c6829d68a9660aa94c2b5547429ac47a35708a25e7b8af2791455eb6cbd1` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-BD-r1.json` | `e372cae0c6c4202227837fc37d31fe93aaadbf6ffd9398277354f6b044b5c2bb` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-BD-r2.json` | `c9ae963117891681f6c30c826b82cc2d08168c2d535e7e44c71d9614ea75c123` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-CD-r1.json` | `fb307c7f18350a2d0edbbadcbd775e6f032473335c6f9288b30d7591dbef0d7e` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-CD-r2.json` | `0b4a258d0ef857d4bb22263e98b0ee60bef6ec0fec3dd95d689837261129bc2c` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-free-r1.json` | `89bf376cf253fbe726b173afe51556d67989301eaa8679bc91047d074db83368` |
| `sprint/trial_run/system_issue/d1-honest-equivalence-free-r2.json` | `df00048392864c880091a45c6f7fb9b52e24e1314a36442a9fa9f198debac3a6` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AB-r1.json` | `d51dae05520b7fb13e449447ed9ecb65f5e729967453e0412c8bbcea1fd203e1` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AB-r2.json` | `efa71932a43f501578973f1c0232f1fd10a9d3897bda5a0c0d221e752e009562` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AC-r1.json` | `ca8610513670f24a54291eaa412ae924dcd87349e4535422a5cfafaa9c4457d6` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AC-r2.json` | `320613661f70ccb6a25a817bd96645081d9478fca13ab20a7dec24986b0fb056` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AD-r1.json` | `edbf1899b459b9270d491dab05722f5124cf12cc32b54dc1321af2913c58811a` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-AD-r2.json` | `d6262f85b947757417d34e24a7317b3e0bf52e3af89a1b47a3c5b4de1fc61b2d` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-BC-r1.json` | `cb9248de27762de501de08018586aa6309b76e31a81d002fc911abb65d49070f` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-BC-r2.json` | `22f23b74e25b706139b1ef1701dfa19643fa84a8d3bf1dc50203cf3f8d65d09e` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-BD-r1.json` | `982640796c41891bf5ad0247eda29baa220bb9aeef70985387e85fd3b4d7347c` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-BD-r2.json` | `d76033d8dce3d545dc05e4442e952724b2592613375ef3dda5026c9a2c7effe4` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-CD-r1.json` | `67343209b6d2ed5078e078947fba14ec7b9ab88f3a8459bebd165cf08622e764` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-CD-r2.json` | `e15795ea9de7d2eedb43ab71c03034dd013db91aec48759c2a528b8bd6dde9b2` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-free-r1.json` | `51ce252e1dffd17b34c04c7080d2cdf90203c718393ee050b61fe6fc858a49d8` |
| `sprint/trial_run/system_issue/d1-reserve-heldout-summarize-free-r2.json` | `13cadeb4fbbc84e4228c1455bda4dafc3c015677f9f67925dd81e16e450328fb` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AB-r1.json` | `5a64de6f28a80a5ae72dcf92360cd06edd0a0fe16fc2f7baa7ef7d868fc5f5f1` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AB-r2.json` | `22ea363f936dda33a08008d2ab69b3c611155bb47a43a097d407505701ba8451` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AC-r1.json` | `798ec6bcad00c178f66628de18cc75ab16a6812f80237721cf2514119a75f437` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AC-r2.json` | `7393c8fa8b200a9ea9de5a09df7111f96d20a711ae04ec64303207495fe18dff` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AD-r1.json` | `dc8a663efcfc2a5e9c8feaa330bfd17cfcc589691d969425b3e12a69c7f17a18` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-AD-r2.json` | `9dda0535aede3e337c3ef4f2fc56c68384e2bae44145f666f6381b1181958661` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-BC-r1.json` | `2f528e6b1bbed92ff3df1793e160e89705371b506cfd7f2708a0bd7cb2657359` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-BC-r2.json` | `3df0b505a4edb324c7d4466ddf60a6e5b8e3621c86f610483bb6566d67a3904e` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-BD-r1.json` | `3382db11009d32336e1d34b543e360e9f1daa0520e998e98eb577149af656709` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-BD-r2.json` | `639f7d9fb44c7608bff87f044376851c50945b68fd9838fe84104326d27c8e53` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-CD-r1.json` | `833326abc1cce0233460eaec03545b523141d8182ef3b5ade93a740b16f7feed` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-CD-r2.json` | `d9c6aff26702a4b5eff3b9c1b31196eddb30c7c13fa913f4b87b92e2116a86ab` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-free-r1.json` | `7fbe49c14512f2b9e9062638e6fe9173e815fd12e9d8b88c6eb699523e337895` |
| `sprint/trial_run/system_issue/d1-reserve-honest-summarize-free-r2.json` | `c1cc7ce0151cb18761c3389bca86e821d9d6381c1749f8d384ababe9b74dab8d` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AB-r1.json` | `97e1fd649bfb2a33bbee5ca443aa38ff0720fbb59716f29a890b3ab9a0029306` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AB-r2.json` | `1f734b49f947ec6bf001447dd899a1b7e694286c2e29238b749f1520d30e94f4` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AC-r1.json` | `260157c49db2732cfcb039cb8c8963395b391a33580bb7cbb3e43e674834cf9e` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AC-r2.json` | `c4ac50429cdb5707c0067e5dbeb8f1c9eec2e17ae4bb8f3b8f16c67042f01bce` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AD-r1.json` | `0e09dc23e648cad8bfe7a925928adcedd1519b8610976044aa48cf43206d6ef7` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-AD-r2.json` | `e5feb0369d52383525d77ff9ed3710f802a7335e169cf68d1cb630a5aca4232e` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-BC-r1.json` | `fc460de374a3a4528f4320f61097921631b1597057b42c52361bca2e3922402f` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-BC-r2.json` | `1104872dc4f74038b3ab061ed7e25fab9d3875daaa66accdd2b56cbf1c274822` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-BD-r1.json` | `2e41c9e2e05dbf7804d287eaf9240427be188dead1413e2a019dd93147df6acc` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-BD-r2.json` | `a703fe386b1fa59f4b3b8aa928d2dc93fb2e8d2378201e69e4c284a950e84720` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-CD-r1.json` | `14b46b892aead97548079b590a4897687e409ac82942f06fcb5a9b874627a1c9` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-CD-r2.json` | `b2e70009275b5e600824ca3f80b96ea71f52549e24cd9ff5769a2e4ec5b9d75c` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-free-r1.json` | `f105272c1e216f7343d1cd02a7a00661eb782a2f5f8d87fa84637af368a9aa6b` |
| `sprint/trial_run/system_issue/d1-reserve-study-parse-assignment-free-r2.json` | `b7e616109c0316ba1deb0c567f29f74527613a6228b4406fdd357ea146c41e5e` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AB-r1.json` | `085ee50d731fa171376741f9c9e036c666805feab749ad7d0e9a0856520cfc1b` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AB-r2.json` | `44bb6e3356a53c5578edae396c4a79d4830c6c7c60d99dc92937d47c2cb88ed5` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AC-r1.json` | `4564f73e1017fc4a0b5c8ba770874764cf5c1ec09bf6289f84f726bedfaa6c26` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AC-r2.json` | `78f56d0e28242c323ad07969cadc0621e53b3b1427a864012462046d41759e75` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AD-r1.json` | `ed27a798c0fdd6885c78eaf7586050e42dfe5407deba8561bc89b8d43755f863` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-AD-r2.json` | `d36fd711133b080b991697fba6ca633b683bb9ceee56f64a0e4f8b171df36149` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-BC-r1.json` | `639192d248ef41895949f4b36f386cd23965199c5c642a99c7d4ab90a3191626` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-BC-r2.json` | `50e07f380e78621173da29e3946ecdffe8aa8dd731c9fbeafebe7d632dbafffe` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-BD-r1.json` | `377bb9dabfc19528159f1e508244be3f820c22de1d31c23e9ed423cf27c19b95` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-BD-r2.json` | `9ccd2f422a57a8d7c13e61a36c5286fd08eb837cbe5e4e31cd21d740bb47e659` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-CD-r1.json` | `d2fe3b824717c8511219756d2a82ddf6a578f68500dc696e47625c821e4d08ae` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-CD-r2.json` | `8d269e11e9396fcf3f5670824076047b7082de8d9ab5b520a4b5a40734bdef9b` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-free-r1.json` | `260213577a7d1f87e310aea443c3956093a34cd3212a6a7397ab4d19b57c2218` |
| `sprint/trial_run/system_issue/d1-reserve-visibility-summary-free-r2.json` | `efc14d868932955f96801d3eb4453de6118bdf90c5cd5c45b9ef3ebb79f6aecb` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-AB-r2.json` | `5ac86937b8e29c3040500ae46b714884b9585a0c34b0a4f930c83f361cec1331` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-AC-r2.json` | `182cb78515c0abc50c182221ec7f271615e9b404f8c3480b739bb71f6fa6a4a7` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-AD-r1.json` | `17620bc956624e4012f57d9e82f3213d188990a669d14cf3f571038669f2292f` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-AD-r2.json` | `ea0d85e70370059141404b658051c3ced4e40a4f11a41f57da735d8972f62ded` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-BC-r1.json` | `956001cdf92aaafc2cd8524f773167b926e8d5b424a7cef264fce89ebcee5463` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-BC-r2.json` | `6c4aa8b12b59b14fedead59625f729a6b0a7841cba63cc6dba9320fb02959cd6` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-BD-r1.json` | `13d1ab9dd14d5e9a38e55f0b1977f8452b879a927da951edabc4531c72001710` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-BD-r2.json` | `95bed721a434948f81d0f6ef203bdea69940f2ff82ad927a6d8d399430b83829` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-CD-r1.json` | `313c06ded7da08a57c9310f879ac110a2ab41e55658fd4e8858ea3b3e64ee4c0` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-CD-r2.json` | `1fb64c9100b4ac611c5f9d6d86becd662b75cf64ab0c4929ed3fe9b2e9cc5433` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-free-r1.json` | `2f47da751b78c49612bd826bfe52aefea4bb4e5ce7e8c324c47292795966f51b` |
| `sprint/trial_run/system_issue/d1-study-ensure-published-free-r2.json` | `1898e433d6a5828bd4823b6b3c199c34f783c5d28ad1ebd4c5391d4a1cf3914e` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AB-r1.json` | `a192d81cc303794a222477a624ce8379594ecceb4aa4413b524ff7699b95fa08` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AB-r2.json` | `270d0f13ab613fb09308c512d4fc1fae3c30b820dbe4f2db247b2b5812c1a6a6` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AC-r1.json` | `fd3c3f782195a37bfc9a9ad73a5764f0ac8044f7585eeabb454294c713ae69a6` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AC-r2.json` | `bf4aefcca4b0bb51390a188cc7d2b8cea25fba7bc974a4aefbfa26c8653b49ed` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AD-r1.json` | `7a314ccd8f7e7d20abffa450e5647694e9051602524e65f4284958daa9d648ba` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-AD-r2.json` | `26f443d324b7affa90faf3180145a71b96041c8721b9d7b064815f7c5926345c` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-BC-r1.json` | `6ce407c5c78d948bc5a3e7ccca14c59778a77a9096d5ce70903a2e9d57405636` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-BC-r2.json` | `dcc90cfc7b2e4c8f001041286dbce5caf0ba61d9d8781b438151fbc330e59c26` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-BD-r1.json` | `81b49c03993896b70bc21f7c2294c03bc7386a1f12447d0fba9ed3d62eab13e9` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-BD-r2.json` | `bf7537c5035d01d0238f31064b6bde034b3c6d0a065ff5c81521eed45ebf99ed` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-CD-r1.json` | `d6093e918b6e0908c1b3381ee34bb824aed4a8411f6be3ac1f5da9b144ee661c` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-CD-r2.json` | `376a772b1a8e2bd39ed183841d07e96e767548f01b26a5af7b6a1b4996c827d4` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-free-r1.json` | `03cca657d27da3e92157dd1c9b8fa33b3eab1e7e148b86c852283afebe8ba1ab` |
| `sprint/trial_run/system_issue/d1-visibility-validate-registration-free-r2.json` | `0e928b10ecc6cf803e6edda7cad34b6f43a8f8b1f5c3a1d47e359078832e50b0` |
