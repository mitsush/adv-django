import React from 'react';
import { Search, MapPin, Upload, Star, Users } from 'lucide-react';
import Layout from '../components/Layout';
import JobCard from '../components/JobCard';

const HomePage = () => {
  // Sample job data - replace with API call
  const jobs = [
    {
      id: 1,
      title: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      type: "Full-time",
      salary: "$120k - $150k",
      skills: ["React", "TypeScript", "GraphQL"],
      posted: "2 days ago"
    },
    // Add more jobs...
  ];

  const features = [
    {
      icon: <Upload className="h-6 w-6" />,
      title: "Easy Resume Upload",
      description: "Upload your resume once and apply to multiple jobs with a single click"
    },
    {
      icon: <Search className="h-6 w-6" />,
      title: "Smart Job Matching",
      description: "Our AI-powered system matches your skills with the most relevant opportunities"
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "Company Insights",
      description: "Learn about company culture, benefits, and employee reviews before applying"
    },
    {
      icon: <Star className="h-6 w-6" />,
      title: "Career Growth",
      description: "Access career resources, salary guides, and professional development content"
    }
  ];

  return (
    <Layout>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
              Find Your Dream Job
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-blue-100 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              Connect with top employers and discover opportunities that match your skills and aspirations
            </p>
            <div className="mt-10 max-w-xl mx-auto">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    type="text"
                    placeholder="Job title, keywords, or company"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border-0 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="flex-1 relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    type="text"
                    placeholder="City, state, or remote"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border-0 focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 font-medium">
                  Search Jobs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Job Listings Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Latest Job Opportunities</h2>
            <p className="mt-1 text-gray-600">Browse {jobs.length} open positions</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map(job => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">Why Choose JobPortal</h2>
            <p className="mt-4 text-lg text-gray-600">Discover the benefits of using our platform</p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {features.map((feature, index) => (
              <div key={index} className="bg-white p-6 rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                  {feature.icon}
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">{feature.title}</h3>
                <p className="mt-2 text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default HomePage;