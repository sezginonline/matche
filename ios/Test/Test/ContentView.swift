//
//  ContentView.swift
//  Test
//
//  Created by Sezgin Serin on 27.03.2023.
//

import SwiftUI

struct ContentView: View {
    @StateObject var viewModel = TestViewModel()
    
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundColor(.accentColor)
            Text("Hello, world!")
            Text(viewModel.result)
        }
        .padding()
        .onAppear {
            viewModel.fetchData()
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
