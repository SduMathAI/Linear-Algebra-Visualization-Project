import React from 'react'
import 'mafs/core.css'
import 'mafs/font.css'
import VectorAddition from './components/VectorAddition'
import MatrixTransform from './components/MatrixTransform'
import EigenVisualizer from './components/EigenVisualizer'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">AI 辅助线性代数可视化 (AI-Assisted Linear Algebra)</h1>
        <p className="text-gray-600">神经符号协同实验平台 - Math & AI Project</p>
      </header>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section>
          <VectorAddition />
        </section>

        <section>
          <MatrixTransform />
        </section>

        <section className="lg:col-span-2">
          <EigenVisualizer />
        </section>
      </div>

      <footer className="mt-12 text-center text-gray-400 text-sm">
        Developed by Group 10 with Trae AI & Mafs.dev
      </footer>
    </div>
  )
}

export default App
