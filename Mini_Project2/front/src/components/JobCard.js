import React, { useState } from 'react';
import { MapPin, Clock, DollarSign, Bookmark, Briefcase } from 'lucide-react';

const JobCard = ({ job }) => {
  const [isBookmarked, setIsBookmarked] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-200 p-6">
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
            <Briefcase className="h-6 w-6 text-gray-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{job.title}</h3>
            <p className="text-gray-600">{job.company}</p>
            <div className="flex items-center mt-2 text-sm text-gray-500">
              <MapPin className="h-4 w-4 mr-1" />
              {job.location}
              <span className="mx-2">•</span>
              <Clock className="h-4 w-4 mr-1" />
              {job.type}
            </div>
          </div>
        </div>
        <button 
          onClick={() => setIsBookmarked(!isBookmarked)}
          className="p-2 hover:bg-gray-100 rounded-full"
        >
          <Bookmark className={`h-5 w-5 ${isBookmarked ? 'fill-blue-600 text-blue-600' : 'text-gray-400'}`} />
        </button>
      </div>
      
      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {job.skills.map((skill, index) => (
            <span key={index} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
              {skill}
            </span>
          ))}
        </div>
      </div>
      
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center text-gray-600">
          <DollarSign className="h-5 w-5 mr-1" />
          <span>{job.salary}</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-500">{job.posted}</span>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium">
            Apply Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobCard;