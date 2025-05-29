import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import AdminPanel from './pages/AdminPanel';
import Layout from './components/Layout';
import SearchPhotos from './pages/SearchPhotos';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/search-photos" element={<SearchPhotos />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App;
