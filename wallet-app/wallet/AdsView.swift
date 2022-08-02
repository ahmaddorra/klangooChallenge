
import SwiftUI

struct AdsView: View {
    @EnvironmentObject var network: Network

    var body: some View {
        ScrollView {
            VStack(alignment: .leading) {
                Text("w")
//                ForEach(network.ads) { ad in
//                    HStack(alignment:.top) {
//                        Text("\(ad.id)")
//
//                        VStack(alignment: .leading) {
//                            Text(ad.title)
//                                .bold()
//
//                            Text(ad.description.lowercased())
//
//
//                        }
//                    }
//                    .frame(width: 300, alignment: .leading)
//                    .padding()
//                    .background(Color(#colorLiteral(red: 0.6667672396, green: 0.7527905703, blue: 1, alpha: 0.2662717301)))
//                    .cornerRadius(20)
//                }
            }

        }
        .padding(.vertical)
//        .onAppear {
//            network.getAds()
//        }
    }
}
struct AdsView_Previews: PreviewProvider {
    static var previews: some View {
        AdsView()
    }
}
