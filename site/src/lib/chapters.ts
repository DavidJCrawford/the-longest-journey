/** The places the journey stops, and what is known about each.
 *
 *  Every factual claim here is sourced. SPEC §3.3 required that the river's
 *  statutory and cultural standing be researched before any of it was asserted,
 *  and the rule applies to the history and geography too: nothing is written
 *  from memory, and where a claim comes from a single source it is attributed in
 *  the text rather than stated as common knowledge.
 *
 *  `km` is distance downstream from the headwater on Ruapehu, on the same axis
 *  as everything else the site draws.
 */
export interface Chapter {
  km: number;
  eyebrow: string;
  title: string;
  /** Paragraphs, as plain text. `**words**` is set in bold — the only markup,
   *  and the script builds it as elements, never as HTML. */
  body: string[];
  /** Listed under the passage, in the order its claims appear. */
  sources?: { label: string; href: string }[];
  /** The monitoring site whose readings belong beside this passage, named
   *  rather than inferred from distance.
   *
   *  Inferring it went wrong three separate ways: a chapter at kilometre 143.8
   *  missed the site at 143.83 and silently showed one 37 km upstream; the
   *  passage about the mouth displayed Tuakau's numbers under a sentence saying
   *  nobody measures there; and because one series once had seven extra
   *  Hamilton sites the others did not, one panel drew its nitrogen from one site
   *  and another reading from a second while naming only the first. Every figure
   *  under a paragraph now comes from the site that paragraph names. */
  site?: string;
  /** No readings belong here — nobody measures this stretch. */
  noWater?: true;
  /* There used to be a one-sentence `note` for the panel, which had room for
     nothing more. The journey now stops at each chapter and shows the whole
     passage, so the notes went, and the few facts only they carried moved
     into the passages. */
}

export const CHAPTERS: Chapter[] = [
  {
    km: 0,
    noWater: true,
    eyebrow: 'Kilometre 0',
    title: 'A cold stream on Ruapehu',
    body: [
      'The Waikato starts as snowmelt on the eastern side of Ruapehu, about 2,600 metres up and less than two kilometres from the summit. It comes off the mountain as the Mangatoetoenui Stream, and twenty kilometres on it joins the Tongariro River, which carries it down to Lake Taupō.',
      'Ruapehu, Tongariro and Ngāuruhoe are sacred maunga to Ngāti Tūwharetoa. In 1887 their chief, Horonuku Te Heuheu Tūkino IV, signed a deed so that the summits could never be sold. The iwi saw it as a shared duty with the Crown to protect the mountains. Those 2,638 hectares became the heart of Tongariro National Park, the country’s first and the fourth in the world.',
    ],
    sources: [{ label: 'Tongariro mountains protected — NZHistory', href: 'https://nzhistory.govt.nz/tongariro-mountains-gifted-to-crown' }],
  },
  {
    km: 87,
    noWater: true,
    eyebrow: 'Kilometre 87',
    title: 'Taupō-nui-a-Tia — Lake Taupō',
    body: [
      'Lake Taupō is a volcano. It fills a caldera left by eruptions between 50,000 and 22,000 years ago, and the last big one, around 232 CE, threw out 60 to 100 cubic kilometres of ash and rock from a vent under the water south of where Taupō town is now.',
      'Its full name, Te Taupō-nui-a-Tia, comes from the rain cloak of the ancestor Tia. Ngāti Tūwharetoa have long held mana over the lake, and in 1992 the Crown returned the lakebed to them.',
      'Since 2011 the farms around the lake have worked under a cap on how much nitrogen their land can leak into it, with public money paying to cut what reaches the lake by a fifth. The council calls it a novel and unprecedented way to cap and trade pollution that comes off the land. The lake will take a long time to show the results: on its northern side, groundwater can take 40 to 85 years to reach it.',
    ],
    sources: [
      { label: 'Volcanic Plateau places: Lake Taupō — Te Ara', href: 'https://teara.govt.nz/en/volcanic-plateau-places/page-10' },
      { label: 'Variation 5: Lake Taupō catchment — Waikato Regional Council', href: 'https://www.waikatoregion.govt.nz/council/policy-and-plans/regional-plan/protecting-lake-taupo/' },
      { label: 'Water quality in New Zealand: land use and nutrient pollution — Parliamentary Commissioner for the Environment, 2013', href: 'https://pce.parliament.nz/media/dgad2d2m/pce-water-quality-land-use-web-amended.pdf' },
    ],
  },
  {
    km: 106.1,
    site: 'Waikato River at Taupo Control Gates',
    eyebrow: 'Kilometre 106',
    title: 'The control gates',
    body: [
      'The river leaves the lake under a concrete bridge built in the 1940s. Six gates in it decide how much water goes down the river to the hydro stations below, and help manage the river when it floods.',
      'This is the first of thirteen places along the river where the water is tested every month. Just below the gates you can see a black disc seven and a half metres away through the water. That is as clear as the Waikato gets.',
    ],
    sources: [{ label: 'Taupō control gates — Mercury', href: 'https://www.mercury.co.nz/about-us/renewable-energy/hydro-generation/taupo-control-gates' }],
  },
  {
    km: 111.4,
    site: 'Waikato at Reids Farm',
    eyebrow: 'Kilometre 111',
    title: 'Te Taheke Hukahuka — Huka Falls',
    body: [
      'Above the falls the river is about 100 metres wide. Here all of it is squeezed through a gap 20 metres across and drops 11 metres, carrying around 220,000 litres a second.',
      'This is also where the river begins in law. The Waikato-Tainui settlement describes it as “a single indivisible being that flows from Te Taheke Hukahuka to Te Puuaha o Waikato”, and records the Crown’s recognition of the river as a tupuna, an ancestor, with its own mana and mauri.',
    ],
    sources: [
      { label: 'Huka Falls — Living Heritage', href: 'https://www.livingheritage.org.nz/Schools-Stories/Places-of-significant-interest-in-Taupo/Huka-Falls' },
      { label: 'Waikato-Tainui Raupatu Claims (Waikato River) Settlement Act 2010, s 8', href: 'https://www.legislation.govt.nz/act/public/2010/24/en/latest/' },
    ],
  },
  {
    km: 118,
    site: 'Waikato at Reids Farm',
    eyebrow: 'Kilometre 118',
    title: 'Aratiatia, the first dam',
    body: [
      'Since 1964 the river here has gone through the Aratiatia power station, and the rapids below the dam are usually a dry, rocky gorge. A few times a day, at 10, 12 and 2, and at 4 in summer, the gates open and 80,000 litres a second pour back down the old riverbed, just so people can see what the rapids once were.',
      'Aratiatia is the first of eight dams between here and Karāpiro.',
    ],
    sources: [{ label: 'Aratiatia Rapids — Love Taupō', href: 'https://www.lovetaupo.com/en/scenic-attractions/aratiatia-rapids/' }],
  },
  {
    km: 143.8,
    site: 'Waikato River at Ohaaki Br',
    eyebrow: 'Kilometre 144',
    title: 'Ohaaki',
    body: [
      'Thirty-eight kilometres below the gates, the water has already changed. There is nearly twice as much nitrogen in it, and you can see 4.6 metres through it instead of 7.5.',
      'In 2013 the Parliamentary Commissioner for the Environment reported that north of Taupō tens of thousands of hectares of pine forest had been felled and turned into dairy farms. Converting one 36,500-hectare forest in the upper catchment was expected to raise the nitrogen lost from that land seventeen-fold, more than cancelling out a $15 million upgrade to Hamilton’s sewage plant.',
      'Between Wairākei Village and Ātiamuri, 75 kilometres of river, nobody lives on its banks at all. It is predominantly pastoral farmland, and around Reporoa most farms run dairy cattle.',
    ],
    sources: [
      { label: 'Water quality in New Zealand: land use and nutrient pollution — Parliamentary Commissioner for the Environment, 2013', href: 'https://pce.parliament.nz/media/dgad2d2m/pce-water-quality-land-use-web-amended.pdf' },
      { label: 'Volcanic Plateau places: Rotorua to Taupō — Te Ara', href: 'https://teara.govt.nz/en/volcanic-plateau-places/page-7' },
    ],
  },
  {
    km: 235,
    site: 'Waikato River at Waipapa Tailrace',
    eyebrow: 'Kilometre 235',
    title: 'The hydro lakes',
    body: [
      'From Ohaaki to Karāpiro the river steps down through six dams, and behind each one it slows into a lake. Slow water fed with nitrogen and phosphorus grows algae, and the algae cloud it. Waikato Regional Council puts algae behind about half the clarity the river loses between Taupō and Ngāruawāhia.',
      'Over this stretch nitrogen nearly quadruples, from 0.13 to 0.51 milligrams a litre, the biggest rise anywhere on the river. By Karāpiro you can see less than two metres through the water.',
    ],
    sources: [
      { label: 'Nutrient limitation of algal biomass in the Waikato River — WRC TR 2018/44', href: 'https://www.waikatoregion.govt.nz/services/publications/tr201844/' },
      { label: 'Visual clarity of the Waikato and Waipā Rivers — WRC TR 2015/13', href: 'https://www.waikatoregion.govt.nz/services/publications/tr201513/' },
    ],
  },
  {
    km: 290,
    site: 'Waikato River at Karapiro Tailrace',
    eyebrow: 'Kilometre 290',
    title: 'Karāpiro',
    body: [
      'Lake Karāpiro, behind the last of the dams, is a rowing course. The world rowing championships were held here in 1978 and again in 2010, when 67,000 people came to watch.',
      'The dams are hard on tuna, the native eels, which come up the river from the sea as tiny elvers. Every summer the elvers that gather at the foot of Karāpiro Dam are caught and carried up past it, about two million a year, more than anywhere else in New Zealand.',
      'Karāpiro is also a line in law. Above it, the river iwi who share its co-management are Ngāti Tūwharetoa, Raukawa and Te Arawa; below it, Waikato-Tainui.',
    ],
    sources: [
      { label: 'The 2010 world championships — NZHistory', href: 'https://nzhistory.govt.nz/culture/rowing-in-new-zealand/karapiro-world+champs-2010' },
      { label: 'Tuna: elvers and recruitment — NIWA', href: 'https://niwa.co.nz/te-kuwaha-and-maori/tuna-information-resource/tuna-biology-and-ecology/tuna-elvers-and-recruitment' },
      { label: 'Ngāti Tūwharetoa, Raukawa, and Te Arawa River Iwi Waikato River Act 2010', href: 'https://www.legislation.govt.nz/act/public/2010/0119/latest/DLM2921819.html' },
    ],
  },
  {
    km: 326,
    site: 'Waikato River at Narrows Boat Ramp',
    eyebrow: 'Kilometre 326',
    title: 'Kirikiriroa — Hamilton',
    body: [
      'The kirikiri, the free-draining gravelly soil of the river terraces, gave Kirikiriroa its name, and it grew kūmara. Wiremu Puke of Ngaati Wairere tells of kūmara mounds at Chartwell dated to between 1550 and 1625, and of reports from the 1800s of gardens running fourteen miles along the terraces from Ngāruawāhia into what is now the city.',
      'Today 192,100 people live here, seven in ten of everyone who lives on the river. By the time the water reaches them most of its clarity is already gone. Of the 5.8 metres of clarity lost between Taupō and the Narrows, just above the city, all but 30 centimetres went before Karāpiro.',
    ],
    sources: [{ label: 'Kūmara kōrero unearths rich history of Kirikiriroa — Waikato Regional Council', href: 'https://www.waikatoregion.govt.nz/story-hub/kumara-korero-unearths-rich-history-of-kirikiriroa/' }],
  },
  {
    km: 348.1,
    site: 'Waikato River at Horotiu Br',
    eyebrow: 'Kilometre 348',
    title: 'Ngāruawāhia',
    body: [
      'On the point where the Waipā meets the Waikato stands Tūrangawaewae marae, the home of the Kīngitanga. The first Māori King, Pōtatau Te Wherowhero, was crowned at Ngāruawāhia in 1858, and Te Puea Hērangi had the marae built from 1921. Every year since 1896 the Tūrangawaewae Regatta has brought carved waka taua onto the river below it.',
      'The Waipā is the biggest river to join the Waikato, and it carries a lot of silt. Below the confluence silt takes about twice as much of the clarity as algae do, and the water turns from green to brown.',
    ],
    sources: [
      { label: 'Ngāruawāhia — Te Ara', href: 'https://teara.govt.nz/en/waikato-places/page-5' },
      { label: 'Tūrangawaewae Regatta — Ngā Taonga', href: 'https://www.ngataonga.org.nz/explore-stories/stories/new-zealand-history/turangawaewae-regatta/' },
      { label: 'Visual clarity of the Waikato and Waipā Rivers — WRC TR 2015/13', href: 'https://www.waikatoregion.govt.nz/services/publications/tr201513/' },
    ],
  },
  {
    km: 377.5,
    site: 'Waikato River at Rangiriri Br',
    eyebrow: 'Kilometre 377',
    title: 'Rangiriri',
    body: [
      'In November 1863 Kīngitanga forces dug a defensive line across the strip of land between the river and Lake Waikare. On the 20th and 21st about 1,400 British troops attacked around 500 defenders. It was one of the costliest battles of the New Zealand Wars, and losing it opened the Waikato to invasion.',
      'The land confiscated after the war, the raupatu, was settled with Waikato-Tainui in 1995. Their claims over the river itself were settled in 2010.',
    ],
    sources: [
      { label: 'Rangiriri — NZHistory', href: 'https://nzhistory.govt.nz/war/war-in-waikato/rangiriri' },
      { label: 'Waikato Raupatu Claims Settlement Act 1995', href: 'https://www.legislation.govt.nz/act/public/1995/0058/latest/whole.html' },
    ],
  },
  {
    km: 395.7,
    site: 'Waikato River at Rangiriri Br',
    eyebrow: 'Kilometre 396',
    title: 'Whangamarino',
    body: [
      'Five kilometres east is Whangamarino, 7,000 hectares of swamp, fen and peat bog, the second-largest bog and swamp complex in the North Island and a wetland of international importance since 1989. It is also part of the flood control scheme for the lower river.',
      'It has been one of the most important places in the country for the matuku-hūrepo, the Australasian bittern, of which fewer than 1,000 are left in New Zealand. In October 2024 a fire burned through much of their habitat here.',
    ],
    sources: [
      { label: 'Whangamarino Wetland — DOC', href: 'https://www.doc.govt.nz/parks-and-recreation/places-to-go/waikato/places/whangamarino-wetland/' },
      { label: 'Australasian bittern/matuku-hūrepo — DOC', href: 'https://www.doc.govt.nz/nature/native-animals/birds/birds-a-z/australasian-bittern-matuku-hurepo/' },
    ],
  },
  {
    km: 413,
    site: 'Waikato River at Tuakau Br',
    eyebrow: 'Kilometre 413',
    title: 'Tuakau',
    body: [
      'This is the last place the river is tested. Compared with the gates at Taupō, there is ten times the nitrogen in the water and fourteen times the phosphorus, and you can see 65 centimetres through it instead of seven and a half metres.',
      'Watercare draws up to 225 million litres a day from the river near here and treats it for Auckland’s taps.',
      'Te Ture Whaimana, the vision for the river written into law, sets as an objective “the restoration of water quality within the Waikato River so that it is safe for people to swim in and take food from **over its entire length**” (emphasis added).',
    ],
    sources: [
      { label: 'Watercare, 14 July 2021', href: 'https://www.watercare.co.nz/home/about-us/latest-news-and-media/new-water-treatment-plant-near-tuakau-about-to-go-live' },
      { label: 'Te Ture Whaimana, Schedule 2', href: 'https://www.legislation.govt.nz/act/public/2010/24/en/latest/' },
    ],
  },
  {
    km: 443.8,
    noWater: true,
    eyebrow: 'Kilometre 444',
    title: 'Te Puuaha o Waikato — Port Waikato',
    body: [
      'The river reaches the Tasman here after draining 14,474 square kilometres, about a twentieth of New Zealand. Nobody tests the water over its last 31 kilometres.',
      'Out past the bar is the coast of the Māui dolphin. Fewer than 100 are left, and the water between the Manukau Heads and Port Waikato is one of the places they are found.',
    ],
    sources: [{ label: 'Māui dolphin — DOC', href: 'https://www.doc.govt.nz/globalassets/documents/conservation/native-animals/marine-mammals/mauis-dolphin-brochure.pdf' }],
  },
];
