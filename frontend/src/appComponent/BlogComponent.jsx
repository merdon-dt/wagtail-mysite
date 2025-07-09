import React, { useEffect, useState } from 'react';

const BlogComponent = () => {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const data = document.getElementById('posts-data');
    if (data) {
      try {
        const parsed = JSON.parse(data.textContent);
        setPosts(parsed);
      } catch (err) {
        console.error('Error parsing JSON', err);
      }
    }
  }, [])
console.log(posts);

return <div>he y</div>
}
//   return <div>{posts?.map(i => {
//     return (
//       <div key={i.id}>
//         <a href={i.url}>{i.title}</a>
//         <img src={i.image_url} alt={i.image_alt} />
//       </div>
//     )
//   })}BlogComponent is here</div>;
// };

export default BlogComponent;
