import React, { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { Link } from 'react-router-dom';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function SearchPhotos() {
    const [searchText, setSearchText] = useState('');
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [validationError, setValidationError] = useState('');
    const [page, setPage] = useState(1); // Track current page
    const [hasMore, setHasMore] = useState(true); // Track if more results are available
    const containerRef = useRef(null); // Reference to scrollable container

    const handleSearchTextChange = (e) => {
        setSearchText(e.target.value);
        setValidationError('');
    };

    const fetchPhotos = async (isNewSearch = false) => {
        if (!hasMore && !isNewSearch) return; // Stop if no more results
        setError(null);
        setLoading(true);

        try {
            let url = `${API_BASE_URL}/search-photos`;
            let location = '';

            if (!searchText.trim()) {
                setValidationError('Location is required when searching by text');
                setLoading(false);
                return;
            }
            location = searchText.trim();

            url += `?location=${encodeURIComponent(location)}&page=${page}&per_page=100`; // Add pagination params
            const response = await fetch(url);
            const data = await response.json();

            if (response.ok && data.status === 'success') {
                const newResults = data.data;
                setResults((prev) => (isNewSearch ? newResults : [...prev, ...newResults])); // Append or replace
                setHasMore(newResults.length > 0); // Assume 10 items per page; adjust based on backend
                if (!isNewSearch) setPage(newResults.page + 1); // Increment page only for load more
            } else {
                throw new Error(data.error || 'Failed to fetch photos');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = () => {
        setResults([]); // Clear previous results
        setPage(1); // Reset to first page
        setHasMore(true); // Reset hasMore
        fetchPhotos(true); // Fetch with isNewSearch=true
    };

    // Handle scroll to load more
    useEffect(() => {
        const handleScroll = () => {
            if (!containerRef.current || loading || !hasMore) return;
            const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
            if (scrollTop + clientHeight >= scrollHeight - 50) { // 50px threshold
                fetchPhotos(); // Load next page
            }
        };

        const container = containerRef.current;
        if (container) {
            container.addEventListener('scroll', handleScroll);
            return () => container.removeEventListener('scroll', handleScroll);
        }
    }, [loading, hasMore]);

    return (
        <div className="flex flex-col items-center justify-center sm:p-6 space-y-4">
            <h2 className="text-2xl font-semibold mb-4">Search Photos for Pose Ideas</h2>

            <div className="w-2/3 mb-4 flex flex-row gap-2 items-center">
                <input
                    type="text"
                    placeholder="Search by location (e.g., Eiffel Tower)..."
                    value={searchText}
                    onChange={handleSearchTextChange}
                    className={`flex-1 px-4 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${validationError ? 'border-red-500' : 'border-gray-300'
                        }`}
                    required
                />
                {validationError && (
                    <p className="text-sm text-red-600">{validationError}</p>
                )}

                <button
                    type="button"
                    onClick={handleSearch}
                    className={`px-4 py-2 bg-indigo-500 text-white rounded-md font-semibold hover:bg-indigo-600 ${!searchText || loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                    disabled={loading}
                >
                    {loading ? 'Searching...' : <Search className="w-5 h-5" />}
                </button>
            </div>

            {error && (
                <div className="bg-red-100 text-red-700 p-4 rounded-xl mb-4">
                    <p>{error}</p>
                </div>
            )}

            {results.length > 0 && (
                <div
                    ref={containerRef}
                    className="max-h-[500px] overflow-y-auto w-full grid grid-cols-1 sm:grid-cols-4 gap-4 gap-y-6 p-4 bg-white/50 rounded-xl shadow-md"
                >
                    {results.length > 0 &&
                        results.map((image, index) => (
                            <div
                                key={`${image.url}-${index}`} // Ensure unique key
                                className="cursor-pointer overflow-hidden rounded shadow-md bg-white"
                            >
                                <Link to={image.link}>
                                    <img
                                        src={image.url}
                                        alt={image.description}
                                        className="w-full sm:h-[320px] object-cover transform transition-transform duration-300 hover:scale-105"
                                    />
                                </Link>
                                <div className="p-2">
                                    <p className="text-sm text-gray-600 truncate">{image.description}</p>
                                    <p className="text-xs text-gray-500">
                                        Photo by:{' '}
                                        <a
                                            href={image.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-indigo-500 hover:underline"
                                        >
                                            {image.photographer}
                                        </a>
                                    </p>
                                </div>
                            </div>
                        ))}
                    {loading && (
                        <div className="col-span-full text-center py-4">
                            <p>Loading more photos...</p>
                        </div>
                    )}
                    {!hasMore && results.length > 0 && (
                        <div className="col-span-full text-center py-4">
                            <p>No more photos to load</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}